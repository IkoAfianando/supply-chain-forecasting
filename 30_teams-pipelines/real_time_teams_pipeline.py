"""
Real-time Supply Chain Monitoring Pipeline with Microsoft Teams Integration
Kafka-based streaming processor for live supply chain events and forecasting updates
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import pandas as pd
import numpy as np
from pymongo import MongoClient
import redis
import aiohttp
from teams_integration_engine import TeamsIntegrationEngine, SupplyChainAlert, AlertType, AlertPriority


@dataclass
class SupplyChainEvent:
    """Supply chain event data structure for streaming"""
    event_id: str
    event_type: str
    timestamp: datetime
    source_system: str
    data: Dict[str, Any]
    processing_status: str = "pending"
    teams_notification_sent: bool = False


class SupplyChainStreamProcessor:
    """
    Real-time supply chain monitoring with Teams integration
    Processes inventory updates, demand changes, and supplier events
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Kafka configuration
        self.kafka_bootstrap_servers = config.get("kafka_servers", ["localhost:9092"])
        self.consumer_topics = config.get("topics", [
            "inventory-updates",
            "demand-forecasts", 
            "supplier-events",
            "production-schedules",
            "cost-changes"
        ])
        
        # Database connections
        self.mongo_client = None
        self.redis_client = None
        
        # Teams integration
        self.teams_webhook_url = config.get("teams_webhook_url")
        self.teams_engine = None
        
        # Processing metrics
        self.metrics = {
            "events_processed": 0,
            "alerts_generated": 0,
            "teams_notifications_sent": 0,
            "processing_errors": 0,
            "start_time": datetime.utcnow()
        }
        
        # Alert thresholds
        self.thresholds = {
            "inventory_critical": 0.10,  # 10% of normal levels
            "inventory_warning": 0.25,   # 25% of normal levels
            "demand_spike": 1.50,        # 50% above normal
            "cost_variance": 0.15,       # 15% cost change
            "supplier_delay": 24         # 24+ hours delay
        }
        
    async def initialize(self):
        """Initialize all connections and services"""
        try:
            # Initialize database connections
            await self._init_databases()
            
            # Initialize Teams integration
            await self._init_teams_integration()
            
            # Initialize Kafka consumer
            self._init_kafka_consumer()
            
            self.logger.info("Supply chain stream processor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            raise
    
    async def _init_databases(self):
        """Initialize MongoDB and Redis connections"""
        
        # MongoDB for persistent storage
        mongo_url = self.config.get("mongodb_url", "mongodb://localhost:27017")
        self.mongo_client = MongoClient(mongo_url)
        self.db = self.mongo_client[self.config.get("database_name", "supply_chain")]
        
        # Redis for real-time caching
        redis_host = self.config.get("redis_host", "localhost")
        redis_port = self.config.get("redis_port", 6379)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
        # Test connections
        self.mongo_client.admin.command('ping')
        self.redis_client.ping()
        
        self.logger.info("Database connections established")
    
    async def _init_teams_integration(self):
        """Initialize Microsoft Teams integration"""
        if self.teams_webhook_url:
            self.teams_engine = TeamsIntegrationEngine(self.teams_webhook_url)
            await self.teams_engine.__aenter__()
            self.logger.info("Teams integration initialized")
        else:
            self.logger.warning("Teams webhook URL not configured - notifications disabled")
    
    def _init_kafka_consumer(self):
        """Initialize Kafka consumer for supply chain events"""
        
        consumer_config = {
            'bootstrap_servers': self.kafka_bootstrap_servers,
            'group_id': 'supply-chain-teams-integration',
            'auto_offset_reset': 'latest',
            'enable_auto_commit': True,
            'value_deserializer': lambda x: json.loads(x.decode('utf-8'))
        }
        
        self.consumer = KafkaConsumer(*self.consumer_topics, **consumer_config)
        self.logger.info(f"Kafka consumer initialized for topics: {self.consumer_topics}")
    
    async def start_processing(self):
        """Start the main event processing loop"""
        
        self.logger.info("Starting supply chain event processing...")
        
        try:
            while True:
                # Process Kafka messages
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        await self._process_event(message)
                
                # Periodic health checks and metrics updates
                await self._update_metrics()
                
                # Small delay to prevent CPU overload
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("Processing stopped by user")
        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
            raise
        finally:
            await self._cleanup()
    
    async def _process_event(self, message) -> bool:
        """Process individual supply chain event"""
        
        try:
            # Parse event data
            event_data = message.value
            topic = message.topic
            
            # Create supply chain event object
            event = SupplyChainEvent(
                event_id=event_data.get("event_id", f"{topic}_{datetime.utcnow().timestamp()}"),
                event_type=topic,
                timestamp=datetime.fromisoformat(event_data.get("timestamp", datetime.utcnow().isoformat())),
                source_system=event_data.get("source", "unknown"),
                data=event_data
            )
            
            # Store event in MongoDB
            await self._store_event(event)
            
            # Analyze event for alerts
            alerts = await self._analyze_event_for_alerts(event)
            
            # Send Teams notifications for alerts
            for alert in alerts:
                if self.teams_engine:
                    success = await self.teams_engine.send_supply_chain_alert(alert)
                    if success:
                        event.teams_notification_sent = True
                        self.metrics["teams_notifications_sent"] += 1
            
            # Update processing metrics
            self.metrics["events_processed"] += 1
            self.metrics["alerts_generated"] += len(alerts)
            
            # Update event status
            event.processing_status = "completed"
            await self._update_event_status(event)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Event processing failed: {str(e)}")
            self.metrics["processing_errors"] += 1
            return False
    
    async def _store_event(self, event: SupplyChainEvent):
        """Store event in MongoDB for historical analysis"""
        
        try:
            collection = self.db.supply_chain_events
            event_doc = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "source_system": event.source_system,
                "data": event.data,
                "processing_status": event.processing_status,
                "teams_notification_sent": event.teams_notification_sent,
                "created_at": datetime.utcnow()
            }
            
            collection.insert_one(event_doc)
            
            # Also cache in Redis for fast access
            cache_key = f"event:{event.event_id}"
            self.redis_client.setex(
                cache_key, 
                timedelta(hours=24), 
                json.dumps(event_doc, default=str)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store event {event.event_id}: {str(e)}")
    
    async def _analyze_event_for_alerts(self, event: SupplyChainEvent) -> List[SupplyChainAlert]:
        """Analyze event and generate supply chain alerts"""
        
        alerts = []
        
        try:
            # Route to appropriate analyzer based on event type
            if event.event_type == "inventory-updates":
                alerts.extend(await self._analyze_inventory_event(event))
            elif event.event_type == "demand-forecasts":
                alerts.extend(await self._analyze_demand_event(event))
            elif event.event_type == "supplier-events":
                alerts.extend(await self._analyze_supplier_event(event))
            elif event.event_type == "cost-changes":
                alerts.extend(await self._analyze_cost_event(event))
            elif event.event_type == "production-schedules":
                alerts.extend(await self._analyze_production_event(event))
            
        except Exception as e:
            self.logger.error(f"Alert analysis failed for event {event.event_id}: {str(e)}")
        
        return alerts
    
    async def _analyze_inventory_event(self, event: SupplyChainEvent) -> List[SupplyChainAlert]:
        """Analyze inventory update events for shortage alerts"""
        
        alerts = []
        data = event.data
        
        try:
            material = data.get("material_category", "Unknown")
            current_level = float(data.get("current_level", 0))
            normal_level = float(data.get("normal_level", 100))
            reorder_point = float(data.get("reorder_point", 20))
            
            # Calculate inventory ratio
            inventory_ratio = current_level / normal_level if normal_level > 0 else 0
            
            # Critical shortage alert
            if inventory_ratio <= self.thresholds["inventory_critical"]:
                alert = SupplyChainAlert(
                    alert_id=f"INV-CRIT-{event.event_id}",
                    alert_type=AlertType.MATERIAL_SHORTAGE,
                    priority=AlertPriority.CRITICAL,
                    title=f"Critical Material Shortage: {material}",
                    description=f"Inventory level critically low at {current_level} units ({inventory_ratio:.1%} of normal)",
                    material_category=material,
                    current_value=current_level,
                    threshold_value=reorder_point,
                    impact_assessment=f"Production halt risk within 24-48 hours. Immediate procurement required.",
                    recommended_actions=[
                        f"Initiate emergency procurement for {material}",
                        "Contact backup suppliers for immediate delivery",
                        "Assess production schedule impact",
                        "Consider alternative materials if available"
                    ],
                    affected_orders=data.get("affected_orders", []),
                    estimated_cost_impact=float(data.get("shortage_cost_impact", 50000)),
                    urgency_deadline=datetime.utcnow() + timedelta(hours=24),
                    responsible_team="Procurement Team"
                )
                alerts.append(alert)
                
            # Warning level shortage
            elif inventory_ratio <= self.thresholds["inventory_warning"]:
                alert = SupplyChainAlert(
                    alert_id=f"INV-WARN-{event.event_id}",
                    alert_type=AlertType.MATERIAL_SHORTAGE,
                    priority=AlertPriority.HIGH,
                    title=f"Material Shortage Warning: {material}",
                    description=f"Inventory level below warning threshold at {current_level} units ({inventory_ratio:.1%} of normal)",
                    material_category=material,
                    current_value=current_level,
                    threshold_value=reorder_point,
                    impact_assessment=f"Reorder recommended within 3-5 days to avoid production delays.",
                    recommended_actions=[
                        f"Schedule procurement order for {material}",
                        "Review demand forecast for accurate quantities",
                        "Coordinate with production planning team"
                    ],
                    affected_orders=data.get("affected_orders", []),
                    estimated_cost_impact=float(data.get("potential_cost_impact", 15000)),
                    urgency_deadline=datetime.utcnow() + timedelta(days=3),
                    responsible_team="Supply Chain Team"
                )
                alerts.append(alert)
        
        except Exception as e:
            self.logger.error(f"Inventory analysis failed: {str(e)}")
        
        return alerts
    
    async def _analyze_demand_event(self, event: SupplyChainEvent) -> List[SupplyChainAlert]:
        """Analyze demand forecast events for spike alerts"""
        
        alerts = []
        data = event.data
        
        try:
            forecasted_demand = float(data.get("forecasted_demand", 0))
            historical_average = float(data.get("historical_average", 100))
            demand_ratio = forecasted_demand / historical_average if historical_average > 0 else 1
            
            # Demand spike alert
            if demand_ratio >= self.thresholds["demand_spike"]:
                alert = SupplyChainAlert(
                    alert_id=f"DEMAND-SPIKE-{event.event_id}",
                    alert_type=AlertType.DEMAND_SPIKE,
                    priority=AlertPriority.HIGH,
                    title="Significant Demand Increase Detected",
                    description=f"Forecasted demand {demand_ratio:.1%} above historical average",
                    material_category=data.get("material_category", "Multiple"),
                    current_value=forecasted_demand,
                    threshold_value=historical_average * self.thresholds["demand_spike"],
                    impact_assessment=f"Inventory shortfall risk. Additional procurement may be required.",
                    recommended_actions=[
                        "Review current inventory levels against increased demand",
                        "Accelerate planned procurement orders",
                        "Contact suppliers for capacity availability",
                        "Assess production capacity constraints"
                    ],
                    affected_orders=data.get("related_orders", []),
                    estimated_cost_impact=float(data.get("additional_cost", 25000)),
                    urgency_deadline=datetime.utcnow() + timedelta(days=7),
                    responsible_team="Demand Planning Team"
                )
                alerts.append(alert)
        
        except Exception as e:
            self.logger.error(f"Demand analysis failed: {str(e)}")
        
        return alerts
    
    async def _analyze_supplier_event(self, event: SupplyChainEvent) -> List[SupplyChainAlert]:
        """Analyze supplier events for delay alerts"""
        
        alerts = []
        data = event.data
        
        try:
            event_type = data.get("supplier_event_type", "")
            delay_hours = float(data.get("delay_hours", 0))
            
            if "delay" in event_type.lower() and delay_hours >= self.thresholds["supplier_delay"]:
                alert = SupplyChainAlert(
                    alert_id=f"SUPPLIER-DELAY-{event.event_id}",
                    alert_type=AlertType.SUPPLIER_DELAY,
                    priority=AlertPriority.HIGH if delay_hours >= 48 else AlertPriority.MEDIUM,
                    title=f"Supplier Delivery Delay: {data.get('supplier_name', 'Unknown')}",
                    description=f"Delivery delayed by {delay_hours} hours for {data.get('material_category', 'materials')}",
                    material_category=data.get("material_category", "Unknown"),
                    current_value=delay_hours,
                    threshold_value=self.thresholds["supplier_delay"],
                    impact_assessment=f"Production schedule impact possible. Alternative sourcing may be needed.",
                    recommended_actions=[
                        "Contact supplier for updated delivery timeline",
                        "Assess impact on production schedule",
                        "Evaluate backup supplier options",
                        "Communicate delays to affected stakeholders"
                    ],
                    affected_orders=data.get("affected_orders", []),
                    estimated_cost_impact=float(data.get("delay_cost_impact", 10000)),
                    urgency_deadline=datetime.utcnow() + timedelta(hours=12),
                    responsible_team="Supplier Relations Team"
                )
                alerts.append(alert)
        
        except Exception as e:
            self.logger.error(f"Supplier analysis failed: {str(e)}")
        
        return alerts
    
    async def _analyze_cost_event(self, event: SupplyChainEvent) -> List[SupplyChainAlert]:
        """Analyze cost change events for variance alerts"""
        
        alerts = []
        data = event.data
        
        try:
            new_cost = float(data.get("new_cost", 0))
            previous_cost = float(data.get("previous_cost", 1))
            cost_variance = abs(new_cost - previous_cost) / previous_cost if previous_cost > 0 else 0
            
            if cost_variance >= self.thresholds["cost_variance"]:
                alert = SupplyChainAlert(
                    alert_id=f"COST-VAR-{event.event_id}",
                    alert_type=AlertType.COST_VARIANCE,
                    priority=AlertPriority.MEDIUM,
                    title=f"Significant Cost Variance: {data.get('material_category', 'Material')}",
                    description=f"Cost change of {cost_variance:.1%} detected",
                    material_category=data.get("material_category", "Unknown"),
                    current_value=new_cost,
                    threshold_value=previous_cost * (1 + self.thresholds["cost_variance"]),
                    impact_assessment=f"Budget impact assessment required. Procurement strategy review recommended.",
                    recommended_actions=[
                        "Review budget impact of cost change",
                        "Evaluate alternative suppliers",
                        "Assess contract renegotiation options",
                        "Update procurement forecasts"
                    ],
                    affected_orders=data.get("affected_orders", []),
                    estimated_cost_impact=float(data.get("budget_impact", 5000)),
                    urgency_deadline=datetime.utcnow() + timedelta(days=5),
                    responsible_team="Procurement Team"
                )
                alerts.append(alert)
        
        except Exception as e:
            self.logger.error(f"Cost analysis failed: {str(e)}")
        
        return alerts
    
    async def _analyze_production_event(self, event: SupplyChainEvent) -> List[SupplyChainAlert]:
        """Analyze production schedule events"""
        
        alerts = []
        # Production event analysis would be implemented here
        return alerts
    
    async def _update_event_status(self, event: SupplyChainEvent):
        """Update event processing status"""
        
        try:
            collection = self.db.supply_chain_events
            collection.update_one(
                {"event_id": event.event_id},
                {
                    "$set": {
                        "processing_status": event.processing_status,
                        "teams_notification_sent": event.teams_notification_sent,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        except Exception as e:
            self.logger.error(f"Failed to update event status: {str(e)}")
    
    async def _update_metrics(self):
        """Update processing metrics in Redis"""
        
        try:
            # Calculate processing rate
            runtime = (datetime.utcnow() - self.metrics["start_time"]).total_seconds()
            processing_rate = self.metrics["events_processed"] / runtime if runtime > 0 else 0
            
            # Update metrics in Redis
            metrics_key = "supply_chain_processor:metrics"
            metrics_data = {
                **self.metrics,
                "processing_rate_per_second": processing_rate,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            self.redis_client.setex(
                metrics_key,
                timedelta(hours=1),
                json.dumps(metrics_data, default=str)
            )
            
        except Exception as e:
            self.logger.error(f"Metrics update failed: {str(e)}")
    
    async def _cleanup(self):
        """Clean up resources"""
        
        try:
            if self.teams_engine:
                await self.teams_engine.__aexit__(None, None, None)
            
            if self.consumer:
                self.consumer.close()
            
            if self.mongo_client:
                self.mongo_client.close()
                
            if self.redis_client:
                self.redis_client.close()
                
            self.logger.info("Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")


# Health monitoring and management functions
async def get_processor_health() -> Dict[str, Any]:
    """Get current processor health status"""
    
    try:
        redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        metrics_data = redis_client.get("supply_chain_processor:metrics")
        
        if metrics_data:
            metrics = json.loads(metrics_data)
            return {
                "status": "healthy",
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "unknown",
                "message": "No metrics available",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Example configuration and startup
async def main():
    """Main function to start the supply chain stream processor"""
    
    config = {
        "kafka_servers": ["localhost:9092"],
        "mongodb_url": "mongodb://localhost:27017",
        "database_name": "supply_chain_forecasting",
        "redis_host": "localhost",
        "redis_port": 6379,
        "teams_webhook_url": "https://your-company.webhook.office.com/webhookb2/...",
        "topics": [
            "inventory-updates",
            "demand-forecasts",
            "supplier-events",
            "production-schedules",
            "cost-changes"
        ]
    }
    
    # Initialize and start processor
    processor = SupplyChainStreamProcessor(config)
    
    try:
        await processor.initialize()
        await processor.start_processing()
    except KeyboardInterrupt:
        logging.info("Processor stopped by user")
    except Exception as e:
        logging.error(f"Processor failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the processor
    asyncio.run(main())
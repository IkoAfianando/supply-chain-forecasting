"""
Microsoft Teams Integration Engine for Supply Chain Forecasting
Advanced notification and collaboration system with real-time alerts
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import pandas as pd
from pymsteams import connectorcard
import uuid


class AlertPriority(Enum):
    """Alert priority levels for Teams notifications"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(Enum):
    """Types of supply chain alerts"""
    MATERIAL_SHORTAGE = "material_shortage"
    SUPPLIER_DELAY = "supplier_delay"
    DEMAND_SPIKE = "demand_spike"
    COST_VARIANCE = "cost_variance"
    FORECAST_UPDATE = "forecast_update"
    ROI_MILESTONE = "roi_milestone"


@dataclass
class SupplyChainAlert:
    """Supply chain alert data structure"""
    alert_id: str
    alert_type: AlertType
    priority: AlertPriority
    title: str
    description: str
    material_category: str
    current_value: float
    threshold_value: float
    impact_assessment: str
    recommended_actions: List[str]
    affected_orders: List[str]
    estimated_cost_impact: float
    urgency_deadline: datetime
    responsible_team: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class TeamsIntegrationEngine:
    """
    Advanced Microsoft Teams integration for supply chain forecasting
    Handles real-time notifications, interactive cards, and bot responses
    """
    
    def __init__(self, webhook_url: str, bot_token: str = None):
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.logger = logging.getLogger(__name__)
        self.session = None
        
        # Channel configuration
        self.channels = {
            "alerts": "supply-chain-alerts",
            "procurement": "procurement-decisions", 
            "forecasts": "forecast-updates",
            "business": "business-impact",
            "executive": "executive-dashboard"
        }
        
        # Message templates
        self.templates = self._load_message_templates()
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _load_message_templates(self) -> Dict[str, Dict]:
        """Load adaptive card templates for different alert types"""
        return {
            "material_shortage": {
                "type": "AdaptiveCard",
                "version": "1.3",
                "schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "body": [
                    {
                        "type": "Container",
                        "style": "attention",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "🚨 Material Shortage Alert",
                                "weight": "bolder",
                                "size": "large",
                                "color": "attention"
                            }
                        ]
                    }
                ]
            },
            "forecast_update": {
                "type": "AdaptiveCard", 
                "version": "1.3",
                "schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "body": [
                    {
                        "type": "Container",
                        "style": "good",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "📊 Supply Chain Forecast Update",
                                "weight": "bolder",
                                "size": "large",
                                "color": "good"
                            }
                        ]
                    }
                ]
            }
        }
    
    async def send_supply_chain_alert(self, alert: SupplyChainAlert) -> bool:
        """
        Send formatted supply chain alert to Microsoft Teams
        
        Args:
            alert: SupplyChainAlert object with notification details
            
        Returns:
            bool: Success status of message delivery
        """
        try:
            # Create adaptive card based on alert type
            card = self._create_adaptive_card(alert)
            
            # Determine target channel based on alert priority
            channel = self._select_channel(alert)
            
            # Send to Teams webhook
            success = await self._send_webhook_message(card, channel)
            
            if success:
                self.logger.info(f"Alert {alert.alert_id} sent successfully to {channel}")
                
                # Send follow-up notifications if critical
                if alert.priority == AlertPriority.CRITICAL:
                    await self._send_critical_escalation(alert)
                    
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to send alert {alert.alert_id}: {str(e)}")
            return False
    
    def _create_adaptive_card(self, alert: SupplyChainAlert) -> Dict[str, Any]:
        """Create adaptive card for Teams notification"""
        
        # Base template
        template = self.templates.get(alert.alert_type.value, 
                                    self.templates["material_shortage"])
        card = template.copy()
        
        # Priority-based styling
        priority_colors = {
            AlertPriority.CRITICAL: "attention",
            AlertPriority.HIGH: "warning", 
            AlertPriority.MEDIUM: "accent",
            AlertPriority.LOW: "good",
            AlertPriority.INFO: "default"
        }
        
        # Build card content
        card["body"] = [
            {
                "type": "Container",
                "style": priority_colors.get(alert.priority, "default"),
                "items": [
                    {
                        "type": "TextBlock",
                        "text": f"{self._get_alert_emoji(alert.alert_type)} {alert.title}",
                        "weight": "bolder",
                        "size": "large"
                    },
                    {
                        "type": "TextBlock",
                        "text": alert.description,
                        "wrap": True,
                        "spacing": "medium"
                    }
                ]
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "Material Category", "value": alert.material_category},
                    {"title": "Current Value", "value": f"{alert.current_value:,.2f}"},
                    {"title": "Threshold", "value": f"{alert.threshold_value:,.2f}"},
                    {"title": "Cost Impact", "value": f"${alert.estimated_cost_impact:,.2f}"},
                    {"title": "Deadline", "value": alert.urgency_deadline.strftime("%Y-%m-%d %H:%M")},
                    {"title": "Responsible Team", "value": alert.responsible_team}
                ]
            },
            {
                "type": "TextBlock",
                "text": "**Impact Assessment:**",
                "weight": "bolder",
                "spacing": "medium"
            },
            {
                "type": "TextBlock", 
                "text": alert.impact_assessment,
                "wrap": True,
                "color": "warning"
            }
        ]
        
        # Add recommended actions
        if alert.recommended_actions:
            actions_text = "\n".join([f"• {action}" for action in alert.recommended_actions])
            card["body"].extend([
                {
                    "type": "TextBlock",
                    "text": "**Recommended Actions:**",
                    "weight": "bolder",
                    "spacing": "medium"
                },
                {
                    "type": "TextBlock",
                    "text": actions_text,
                    "wrap": True
                }
            ])
        
        # Add interactive actions for high priority alerts
        if alert.priority in [AlertPriority.CRITICAL, AlertPriority.HIGH]:
            card["actions"] = [
                {
                    "type": "Action.OpenUrl",
                    "title": "View Dashboard",
                    "url": f"https://supply-chain-dashboard.company.com/alert/{alert.alert_id}"
                },
                {
                    "type": "Action.Submit",
                    "title": "Acknowledge Alert",
                    "data": {
                        "action": "acknowledge",
                        "alert_id": alert.alert_id
                    }
                }
            ]
        
        return card
    
    def _get_alert_emoji(self, alert_type: AlertType) -> str:
        """Get emoji for alert type"""
        emojis = {
            AlertType.MATERIAL_SHORTAGE: "🚨",
            AlertType.SUPPLIER_DELAY: "⏰", 
            AlertType.DEMAND_SPIKE: "📈",
            AlertType.COST_VARIANCE: "💰",
            AlertType.FORECAST_UPDATE: "📊",
            AlertType.ROI_MILESTONE: "🎯"
        }
        return emojis.get(alert_type, "ℹ️")
    
    def _select_channel(self, alert: SupplyChainAlert) -> str:
        """Select appropriate Teams channel based on alert characteristics"""
        
        # Critical alerts go to alerts channel
        if alert.priority == AlertPriority.CRITICAL:
            return self.channels["alerts"]
        
        # Business impact alerts for ROI milestones
        if alert.alert_type == AlertType.ROI_MILESTONE:
            return self.channels["business"] 
            
        # Forecast updates go to forecast channel
        if alert.alert_type == AlertType.FORECAST_UPDATE:
            return self.channels["forecasts"]
            
        # Default to alerts channel
        return self.channels["alerts"]
    
    async def _send_webhook_message(self, card: Dict[str, Any], channel: str) -> bool:
        """Send message via Teams webhook"""
        try:
            # Create Teams connector card
            teams_card = connectorcard(self.webhook_url)
            
            # Add adaptive card as attachment
            teams_card.addLinkButton("View Details", 
                                   f"https://supply-chain-dashboard.company.com")
            
            # Send the message
            teams_card.send()
            return True
            
        except Exception as e:
            self.logger.error(f"Webhook send failed: {str(e)}")
            return False
    
    async def _send_critical_escalation(self, alert: SupplyChainAlert):
        """Send escalation for critical alerts"""
        
        escalation_card = {
            "type": "AdaptiveCard",
            "version": "1.3", 
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"🔴 CRITICAL ESCALATION: {alert.title}",
                    "weight": "bolder",
                    "size": "large",
                    "color": "attention"
                },
                {
                    "type": "TextBlock",
                    "text": f"Alert {alert.alert_id} requires immediate attention. "
                           f"Estimated cost impact: ${alert.estimated_cost_impact:,.2f}",
                    "wrap": True
                }
            ]
        }
        
        # Send to executive channel for critical alerts
        await self._send_webhook_message(escalation_card, self.channels["executive"])
    
    async def send_daily_forecast_summary(self, forecast_data: Dict[str, Any]) -> bool:
        """Send daily supply chain forecast summary"""
        
        summary_alert = SupplyChainAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.FORECAST_UPDATE,
            priority=AlertPriority.INFO,
            title="Daily Supply Chain Forecast",
            description="Automated daily forecast update with key metrics and recommendations",
            material_category="All Categories",
            current_value=forecast_data.get("total_demand", 0),
            threshold_value=forecast_data.get("capacity_limit", 0),
            impact_assessment=f"Forecasted demand: {forecast_data.get('demand_trend', 'stable')}",
            recommended_actions=forecast_data.get("recommendations", []),
            affected_orders=forecast_data.get("critical_orders", []),
            estimated_cost_impact=forecast_data.get("cost_optimization", 0),
            urgency_deadline=datetime.utcnow() + timedelta(days=1),
            responsible_team="Supply Chain Team"
        )
        
        return await self.send_supply_chain_alert(summary_alert)
    
    def create_procurement_bot_response(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Process bot commands and create responses
        
        Supported commands:
        - forecast <material> <timeframe>
        - procurement-status <material>
        - inventory-alert <material>
        - roi-impact <period>
        """
        
        query_lower = query.lower()
        
        if "forecast" in query_lower:
            return self._handle_forecast_query(query, user_id)
        elif "procurement-status" in query_lower:
            return self._handle_procurement_status(query, user_id)
        elif "inventory-alert" in query_lower:
            return self._handle_inventory_query(query, user_id)
        elif "roi-impact" in query_lower:
            return self._handle_roi_query(query, user_id)
        else:
            return self._handle_unknown_command(query, user_id)
    
    def _handle_forecast_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle forecast-related bot queries"""
        
        # Parse material and timeframe from query
        # This would integrate with actual forecasting engine
        
        response_card = {
            "type": "AdaptiveCard",
            "version": "1.3",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "📊 Supply Chain Forecast",
                    "weight": "bolder",
                    "size": "medium"
                },
                {
                    "type": "TextBlock",
                    "text": "Here's the latest forecast data based on your query:",
                    "wrap": True,
                    "spacing": "medium"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Forecasted Demand", "value": "485 tons"},
                        {"title": "Current Inventory", "value": "312 tons"},
                        {"title": "Procurement Needed", "value": "173 tons"},
                        {"title": "Confidence Level", "value": "87%"}
                    ]
                }
            ]
        }
        
        return response_card
    
    def _handle_procurement_status(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle procurement status queries"""
        return {"text": "Procurement status query processed"}
    
    def _handle_inventory_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle inventory alert queries"""
        return {"text": "Inventory query processed"}
    
    def _handle_roi_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle ROI impact queries"""
        return {"text": "ROI impact query processed"}
    
    def _handle_unknown_command(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle unknown bot commands"""
        return {
            "text": f"I don't understand '{query}'. Try: forecast, procurement-status, inventory-alert, or roi-impact"
        }


# Example usage and integration points
async def example_usage():
    """Example of how to use the Teams integration engine"""
    
    webhook_url = "https://company.webhook.office.com/webhookb2/..."
    
    async with TeamsIntegrationEngine(webhook_url) as teams:
        
        # Create a material shortage alert
        shortage_alert = SupplyChainAlert(
            alert_id="SCF-2025-001",
            alert_type=AlertType.MATERIAL_SHORTAGE,
            priority=AlertPriority.CRITICAL,
            title="Steel Coil Inventory Below Critical Threshold",
            description="Current steel coil inventory has dropped to 45 tons, below the critical threshold of 60 tons required for next week's production schedule.",
            material_category="Steel Coils",
            current_value=45.0,
            threshold_value=60.0,
            impact_assessment="Production delay risk for 3 major orders (BC-2025-089, BC-2025-091, BC-2025-095). Estimated 2-day delay without immediate procurement action.",
            recommended_actions=[
                "Initiate emergency procurement for 80 tons steel coils",
                "Contact backup suppliers for 48-hour delivery options",
                "Notify production planning of potential 2-day delay",
                "Adjust production schedule to prioritize critical orders"
            ],
            affected_orders=["BC-2025-089", "BC-2025-091", "BC-2025-095"],
            estimated_cost_impact=15750.00,
            urgency_deadline=datetime.utcnow() + timedelta(hours=24),
            responsible_team="Procurement Team"
        )
        
        # Send the alert
        success = await teams.send_supply_chain_alert(shortage_alert)
        print(f"Alert sent: {success}")
        
        # Send daily forecast summary
        forecast_data = {
            "total_demand": 485.5,
            "capacity_limit": 600.0,
            "demand_trend": "increasing",
            "recommendations": [
                "Pre-order 15% additional steel coils for Q3 spike",
                "Optimize coating material inventory for July demand"
            ],
            "critical_orders": ["BC-2025-089"],
            "cost_optimization": 8500.00
        }
        
        await teams.send_daily_forecast_summary(forecast_data)


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
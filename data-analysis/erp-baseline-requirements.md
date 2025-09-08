# ERP Logs Baseline Data Source Requirements

## Current Available ERP Data Sources

### Primary Collections (Production System)

#### 1. Orders Management (`jobs` collection)
**Current Data Structure:**
- `_id`: Unique job identifier
- `name`: Job/order description (e.g., "10x10x4.5C1577BoxCulvert>2")
- `locationId`: Manufacturing location reference
- `partId`: Associated part/product reference
- `machineClassId`: Equipment type requirement
- `factoryId`: Factory assignment
- `priorityStatus`: High/Medium/Low priority classification
- `status`: Active/Completed/Pending status
- `isStock`: Stock vs. custom order flag
- `dueDate`: Delivery deadline
- `createdAt`: Order creation timestamp

**AI Forecasting Usage:**
- Historical order patterns by priority and type
- Seasonal demand analysis from creation dates
- Lead time calculations from creation to completion
- Customer demand pattern recognition

#### 2. Inventory Management (`parts` collection)
**Current Data Structure:**
- `_id`: Part identifier
- `name`: Product specification
- `tons`: Material weight requirements
- `machineClassId`: Production equipment requirements
- `manufactureCost`: Production cost tracking
- `inInventory`: Current stock levels
- `createdAt`: Part catalog entry date
- `deletedAt`: Discontinuation tracking

**AI Forecasting Usage:**
- Material consumption rate calculations
- Product lifecycle analysis
- Cost trend analysis for procurement planning
- Inventory turnover optimization

#### 3. Production Tracking (`timerlogs` collection)
**Current Data Volume:** 125,566+ records across systems
**Data Structure Elements:**
- Production timing data
- Machine utilization patterns
- Operational efficiency metrics
- Production cycle tracking

**AI Forecasting Usage:**
- Production capacity planning
- Lead time prediction accuracy
- Bottleneck identification
- Resource allocation optimization

#### 4. Equipment Management (`machines` collection)
**Current Data Structure:**
- `_id`: Machine identifier
- `name`: Equipment name/type
- `machineClassId`: Equipment classification
- `factoryId`: Location assignment
- `locationId`: Physical location tracking

**AI Forecasting Usage:**
- Production capacity constraints
- Equipment availability planning
- Maintenance impact on scheduling
- Resource allocation optimization

### Missing ERP Integration Points (Placeholder Requirements)

#### 1. Supplier Management System
**Required Fields:**
```json
{
  "supplier_id": "string",
  "supplier_name": "string",
  "material_categories": ["steel_coils", "welding_consumables", "coating_materials"],
  "lead_time_days": "integer",
  "reliability_score": "float (0-1)",
  "geographic_location": "string",
  "payment_terms": "string",
  "minimum_order_quantity": "float",
  "price_per_unit": "float",
  "last_delivery_date": "datetime",
  "quality_rating": "float (0-5)"
}
```

**Placeholder Implementation:**
- Create mock supplier database with 5-10 suppliers per material type
- Generate synthetic lead time data based on industry standards
- Implement reliability scoring based on delivery performance
- Create geographic distribution for shipping cost calculations

#### 2. Material Inventory System
**Required Fields:**
```json
{
  "material_id": "string",
  "material_name": "string",
  "category": "steel_coils|welding_consumables|coating_materials",
  "current_stock_quantity": "float",
  "unit_of_measure": "tons|pounds|gallons",
  "location_id": "string",
  "reorder_point": "float",
  "economic_order_quantity": "float",
  "safety_stock_level": "float",
  "cost_per_unit": "float",
  "last_receipt_date": "datetime",
  "expiration_date": "datetime",
  "quality_grade": "string"
}
```

**Placeholder Implementation:**
- Map existing `parts` collection tonnage to material requirements
- Create synthetic current stock levels based on recent production
- Generate reorder points using 2-week consumption averages
- Implement cost tracking with inflation factors

#### 3. Customer Segmentation System
**Required Fields:**
```json
{
  "customer_id": "string",
  "customer_name": "string",
  "customer_type": "contractors|oil_gas|infrastructure",
  "geographic_region": "string",
  "seasonal_pattern": "object",
  "average_order_size": "float",
  "payment_terms": "string",
  "priority_level": "string",
  "last_order_date": "datetime",
  "order_frequency_days": "integer"
}
```

**Placeholder Implementation:**
- Analyze job names to categorize customer types
- Create seasonal demand patterns based on infrastructure industry standards
- Generate order frequency patterns from historical job data
- Map priority status to customer priority levels

#### 4. Financial Integration System
**Required Fields:**
```json
{
  "transaction_id": "string",
  "transaction_type": "material_purchase|production_cost|storage_cost",
  "material_id": "string",
  "quantity": "float",
  "unit_cost": "float",
  "total_cost": "float",
  "transaction_date": "datetime",
  "supplier_id": "string",
  "currency": "string",
  "exchange_rate": "float"
}
```

**Placeholder Implementation:**
- Use existing `manufactureCost` data as baseline
- Generate material purchase costs using industry pricing
- Create storage and handling cost calculations
- Implement currency conversion for international suppliers

### Real-Time Data Feed Requirements

#### 1. Production Status Updates
**Update Frequency:** Every 15 minutes
**Data Points:**
- Current job progress percentage
- Machine utilization status
- Quality check results
- Material consumption rates
- Estimated completion times

**Integration Method:**
- REST API endpoints from production control systems
- WebSocket connections for real-time updates
- Database triggers for status changes

#### 2. Inventory Level Monitoring
**Update Frequency:** Every hour
**Data Points:**
- Raw material stock levels
- Work-in-progress inventory
- Finished goods inventory
- Material consumption rates
- Incoming delivery schedules

**Integration Method:**
- RFID/barcode scanning integration
- Automated scale readings
- Warehouse management system APIs

#### 3. Supplier Performance Tracking
**Update Frequency:** Daily
**Data Points:**
- Delivery performance metrics
- Quality incident reports
- Price fluctuation tracking
- Lead time variations
- Communication responsiveness

**Integration Method:**
- Supplier portal integration
- EDI transaction monitoring
- Email parsing for delivery notifications

## Baseline Data Quality Requirements

### Data Accuracy Standards
- **Inventory Levels**: ±2% accuracy required
- **Lead Times**: ±10% accuracy for supplier performance
- **Production Rates**: ±5% accuracy for capacity planning
- **Cost Data**: ±3% accuracy for financial projections

### Data Completeness Requirements
- **Order History**: Minimum 24 months of complete records
- **Supplier Performance**: Minimum 12 months of delivery data
- **Production Cycles**: All cycles must have start/end timestamps
- **Material Consumption**: All jobs must have associated material usage

### Data Freshness Requirements
- **Critical Path Items**: Real-time updates (< 5 minutes)
- **Inventory Levels**: Hourly updates maximum
- **Financial Data**: Daily updates acceptable
- **Historical Analysis**: Weekly consolidation sufficient

## Implementation Roadmap

### Phase 1: Baseline Data Establishment (Weeks 1-2)
1. Map existing ERP collections to forecasting requirements
2. Create placeholder data for missing integrations
3. Establish data quality monitoring procedures
4. Implement basic data validation rules

### Phase 2: Real-Time Integration (Weeks 3-4)
1. Develop API connections to existing systems
2. Implement automated data synchronization
3. Create error handling and data recovery procedures
4. Establish monitoring and alerting systems

### Phase 3: Advanced Analytics Integration (Weeks 5-6)
1. Connect forecasting algorithms to data streams
2. Implement predictive model training pipelines
3. Create automated decision-making workflows
4. Establish performance monitoring and optimization

This baseline data source framework ensures the Supply Chain & Order Forecasting AI Profile has access to comprehensive, accurate, and timely information for effective demand prediction and material planning.
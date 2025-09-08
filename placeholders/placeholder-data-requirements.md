# Placeholder Data Requirements for Supply Chain Forecasting

## Data Availability Summary

### Available Data Sources (From MongoDB Dump Analysis)

#### ✅ Complete and Usable Data
1. **Order History (`jobs` collection)**
   - **Records Available**: 2,673 historical + 34 active orders
   - **Quality**: High - Complete timestamps, priorities, specifications
   - **Usage**: Primary demand forecasting input
   - **Fields**: Job names, creation dates, priorities, due dates, part references

2. **Product Specifications (`parts` collection)**
   - **Records Available**: 8,678 parts with material requirements
   - **Quality**: High - Tonnage data, cost tracking, inventory levels
   - **Usage**: Material consumption calculations
   - **Fields**: Tonnage per unit, manufacturing costs, inventory status

3. **Production Tracking (`timerlogs` collection)**
   - **Records Available**: 125K+ production timing records
   - **Quality**: High - Detailed operational timing data
   - **Usage**: Lead time calculations, capacity planning
   - **Fields**: Production timing, machine utilization, cycle data

4. **Equipment Data (`machines` collection)**
   - **Records Available**: 44-57 machine records across systems
   - **Quality**: Medium - Basic machine information available
   - **Usage**: Capacity constraint modeling
   - **Fields**: Machine types, locations, classifications

#### ⚠️ Partially Available Data
1. **Location Information (`locations` collection)**
   - **Records Available**: 3 location records
   - **Quality**: Limited - Basic location data only
   - **Gap**: Geographic distribution, shipping costs, storage capacities
   - **Placeholder Needed**: Detailed location attributes

2. **User/Customer Data (`users` collection)**
   - **Records Available**: 51-78 user records
   - **Quality**: Limited - User management data only
   - **Gap**: Customer segmentation, order patterns, regional data
   - **Placeholder Needed**: Customer classification system

### Missing Data Sources (Require Full Placeholders)

#### ❌ Critical Missing Data

#### 1. Supplier Management System
**Impact**: High - Cannot optimize procurement without supplier data
**Placeholder Requirements:**
```json
{
  "suppliers_placeholder": {
    "steel_coil_suppliers": [
      {
        "supplier_id": "SUP_STEEL_001",
        "name": "Industrial Steel Supply Co.",
        "location": "Pittsburgh, PA",
        "lead_time_days": 21,
        "reliability_score": 0.92,
        "min_order_tons": 50,
        "price_per_ton": 850,
        "grades_available": ["A36", "A572", "A588"],
        "shipping_cost_per_mile": 2.50
      },
      {
        "supplier_id": "SUP_STEEL_002", 
        "name": "Midwest Steel Distribution",
        "location": "Chicago, IL",
        "lead_time_days": 14,
        "reliability_score": 0.88,
        "min_order_tons": 25,
        "price_per_ton": 875,
        "grades_available": ["A36", "A572"],
        "shipping_cost_per_mile": 2.25
      }
    ],
    "welding_suppliers": [
      {
        "supplier_id": "SUP_WELD_001",
        "name": "Welding Supply Warehouse",
        "location": "Houston, TX", 
        "lead_time_days": 7,
        "reliability_score": 0.95,
        "consumable_types": ["ER70S-6", "E7018", "Flux Core"],
        "price_per_pound": 4.25
      }
    ],
    "coating_suppliers": [
      {
        "supplier_id": "SUP_COAT_001",
        "name": "Industrial Coatings Inc.",
        "location": "Atlanta, GA",
        "lead_time_days": 10,
        "reliability_score": 0.90,
        "coating_types": ["Epoxy", "Polyurethane", "Primer"],
        "price_per_gallon": 85.00
      }
    ]
  }
}
```

#### 2. Current Inventory Management
**Impact**: High - Cannot forecast material needs without current stock data
**Placeholder Requirements:**
```json
{
  "inventory_placeholder": {
    "steel_inventory": {
      "A36_coils": {
        "current_stock_tons": 125.5,
        "location": "Primary Staging Area",
        "last_receipt_date": "2024-08-15",
        "avg_monthly_consumption": 89.2,
        "reorder_point_tons": 60.0,
        "safety_stock_tons": 30.0
      },
      "A572_coils": {
        "current_stock_tons": 78.3,
        "location": "Primary Staging Area", 
        "last_receipt_date": "2024-08-20",
        "avg_monthly_consumption": 45.6,
        "reorder_point_tons": 35.0,
        "safety_stock_tons": 20.0
      }
    },
    "welding_inventory": {
      "ER70S-6_wire": {
        "current_stock_pounds": 2850,
        "location": "Climate Controlled Storage",
        "expiration_date": "2025-08-01",
        "avg_monthly_consumption": 1200,
        "reorder_point_pounds": 800
      }
    },
    "coating_inventory": {
      "epoxy_primer": {
        "current_stock_gallons": 145,
        "location": "Hazmat Storage Area",
        "avg_monthly_consumption": 85,
        "shelf_life_months": 12,
        "reorder_point_gallons": 60
      }
    }
  }
}
```

#### 3. Customer Segmentation Data
**Impact**: Medium - Needed for seasonal demand modeling
**Placeholder Requirements:**
```json
{
  "customer_segmentation": {
    "contractors": {
      "seasonal_pattern": {
        "q1_multiplier": 0.8,
        "q2_multiplier": 1.1,
        "q3_multiplier": 1.4,
        "q4_multiplier": 0.7
      },
      "avg_order_size_tons": 45.2,
      "typical_lead_time_weeks": 6,
      "payment_terms": "Net 30"
    },
    "oil_gas": {
      "seasonal_pattern": {
        "q1_multiplier": 1.2,
        "q2_multiplier": 1.0,
        "q3_multiplier": 0.8,
        "q4_multiplier": 1.0
      },
      "avg_order_size_tons": 128.7,
      "typical_lead_time_weeks": 8,
      "payment_terms": "Net 45"
    },
    "infrastructure": {
      "seasonal_pattern": {
        "q1_multiplier": 0.6,
        "q2_multiplier": 1.2,
        "q3_multiplier": 1.8,
        "q4_multiplier": 0.4
      },
      "avg_order_size_tons": 89.3,
      "typical_lead_time_weeks": 10,
      "payment_terms": "Net 60"
    }
  }
}
```

#### 4. Financial and Costing Data
**Impact**: Medium - Required for total cost optimization
**Placeholder Requirements:**
```json
{
  "financial_placeholders": {
    "carrying_costs": {
      "storage_cost_per_ton_per_month": 12.50,
      "insurance_rate_annual": 0.015,
      "obsolescence_rate_annual": 0.02,
      "opportunity_cost_rate": 0.08
    },
    "procurement_costs": {
      "purchase_order_processing_cost": 85.00,
      "receiving_inspection_cost": 125.00,
      "transportation_cost_per_mile_per_ton": 0.45,
      "expedite_premium_percentage": 0.25
    },
    "shortage_costs": {
      "production_delay_cost_per_day": 2500.00,
      "customer_penalty_percentage": 0.02,
      "emergency_sourcing_premium": 0.35
    }
  }
}
```

## Placeholder Implementation Strategy

### Phase 1: Static Placeholder Data (Week 1)
1. **Create Mock Data Files**
   - Generate supplier database with realistic lead times and pricing
   - Create inventory snapshots based on historical consumption patterns
   - Develop customer segmentation based on order analysis
   - Establish financial parameters using industry standards

2. **Data Validation Rules**
   - Ensure placeholder data consistency with existing production data
   - Validate material consumption rates against historical patterns
   - Cross-check supplier lead times with production schedules
   - Verify cost parameters against industry benchmarks

### Phase 2: Dynamic Placeholder Generation (Week 2)
1. **Algorithm-Based Placeholders**
   - Generate dynamic inventory levels based on recent production
   - Create supplier performance variations using probability distributions
   - Simulate seasonal demand patterns using historical job data
   - Model cost fluctuations using market trend algorithms

2. **Integration Testing**
   - Test placeholder data feeds with forecasting algorithms
   - Validate decision tree logic with simulated scenarios
   - Ensure placeholder data updates don't break system operations
   - Verify performance metrics calculations with mock data

### Phase 3: Placeholder-to-Real Data Migration Planning (Week 3)
1. **Migration Framework**
   - Design data replacement procedures for when real integrations are available
   - Create validation tests to ensure real data quality meets placeholder standards
   - Develop rollback procedures if real data integration fails
   - Plan gradual transition from placeholders to live data feeds

2. **Documentation and Handoff**
   - Document all placeholder assumptions and limitations
   - Create mapping documentation for real data integration
   - Establish monitoring alerts for placeholder data inconsistencies

## Quality Assurance for Placeholder Data

### Validation Criteria
1. **Consistency**: Placeholder values must align with existing production data patterns
2. **Completeness**: All critical decision points must have supporting placeholder data
3. **Realism**: Values must reflect actual industry standards and practices
4. **Maintainability**: Placeholder data must be easily updatable as requirements evolve

### Testing Procedures
1. **Unit Testing**: Each placeholder data set tested independently
2. **Integration Testing**: Placeholder data tested with forecasting algorithms
3. **Scenario Testing**: Placeholder data validated against known business scenarios
4. **Performance Testing**: System response times verified with placeholder data volumes

### Monitoring and Updates
1. **Weekly Review**: Placeholder data accuracy reviewed against actual outcomes
2. **Monthly Calibration**: Placeholder parameters adjusted based on business feedback
3. **Quarterly Validation**: Complete placeholder dataset reviewed for continued relevance
4. **Integration Readiness**: Continuous assessment of real data integration opportunities

This placeholder framework ensures the Supply Chain Forecasting system can operate effectively while maintaining clear documentation of limitations and migration paths for future real data integration.
# Supply Chain Procurement & Staging Logic

## Overview
This document outlines the logical framework for how demand forecasting impacts raw material procurement and staging, with specific focus on steel coils, welding consumables, and coating materials for concrete infrastructure manufacturing.

## Data-Driven Insights from Analysis

### Product Categories Identified
Based on the parts analysis (Box Culvert products):
- **Tonnage Range**: 5.716 - 8.574 tons per unit
- **Product Variations**: Different wall thicknesses (2.00, 2.75, 3.0, 4.0, 4.5)
- **Size Variations**: 10x10 standard with different configurations
- **Manufacturing Classification**: C1577 specification standard

### Material Requirements Pattern Analysis

#### Steel Coil Consumption Logic
```
Raw Material Need = (Part Tonnage × Order Quantity × Safety Factor)
Safety Factor = 1.15 (15% waste/scrap allowance)

Example Calculation:
- Box Culvert 10X10X3: 8.574 tons/unit
- Order of 50 units = 428.7 tons raw steel
- With safety factor = 493.0 tons steel coils required
```

#### Welding Consumables Logic
```
Welding Material = (Total Linear Feet of Welds × Wire/Rod Consumption Rate)
Consumption Rate = 2.5 lbs per linear foot (industry standard)

Estimation Logic:
- Box Culvert perimeter welds ≈ 40 linear feet per unit
- 50 units × 40 feet × 2.5 lbs = 5,000 lbs welding consumables
```

#### Coating Materials Logic
```
Coating Need = (Surface Area × Coverage Rate × Coating Layers)
Coverage Rate = 1 gallon per 350 sq ft (epoxy coating standard)

Estimation Logic:
- Box Culvert surface area ≈ 400 sq ft per unit
- 50 units × 400 sq ft ÷ 350 coverage = 57 gallons base coat
- Plus primer and finish coats = 171 gallons total
```

## Seasonal Demand Forecasting Impact

### Q3 Infrastructure Spike Analysis

#### Historical Pattern Recognition (Placeholder Logic)
```python
def calculate_q3_demand_spike():
    # Placeholder for seasonal analysis
    q3_multiplier = 1.4  # 40% increase in Q3
    base_demand = calculate_base_demand()
    
    infrastructure_orders = base_demand * q3_multiplier
    oil_gas_orders = base_demand * 0.8  # 20% decrease in Q3
    contractor_orders = base_demand * 1.1  # 10% increase in Q3
    
    return {
        'infrastructure': infrastructure_orders,
        'oil_gas': oil_gas_orders,
        'contractors': contractor_orders
    }
```

#### Material Procurement Timeline Impact
1. **Lead Time Adjustments**
   - Steel coils: Normal 4-6 weeks → Q2 procurement for Q3 demand
   - Welding consumables: Normal 2-3 weeks → Q2 inventory build-up
   - Coating materials: Normal 1-2 weeks → Just-in-time with Q3 buffer

2. **Inventory Staging Strategy**
   - **Pre-Q3 Buildup (June-July)**
     - Steel coils: 60% of Q3 forecast
     - Welding consumables: 80% of Q3 forecast
     - Coating materials: 40% of Q3 forecast
   
   - **Q3 Active Replenishment (Aug-Sep)**
     - Steel coils: Weekly deliveries to maintain 2-week buffer
     - Welding consumables: Bi-weekly replenishment
     - Coating materials: Weekly replenishment

## Cross-Analysis Prevention Logic

### Shortage Prevention System
```python
def prevent_material_shortages():
    current_inventory = get_current_inventory()
    forecasted_demand = get_30_day_forecast()
    supplier_lead_times = get_supplier_lead_times()
    
    for material in ['steel_coils', 'welding_consumables', 'coating_materials']:
        reorder_point = (forecasted_demand[material] * supplier_lead_times[material]) * 1.2
        
        if current_inventory[material] <= reorder_point:
            trigger_emergency_procurement(material)
            
    return shortage_prevention_actions
```

### Overstock Reduction Logic
```python
def reduce_overstock():
    inventory_turnover_target = 6  # 6 times per year
    current_turnover = calculate_current_turnover()
    
    overstock_threshold = annual_usage / inventory_turnover_target
    
    for material in inventory:
        if inventory[material] > overstock_threshold[material]:
            # Implement consumption acceleration
            prioritize_jobs_using_material(material)
            reduce_future_procurement(material)
            consider_alternative_suppliers(material)
            
    return overstock_reduction_plan
```

### Order Fulfillment Speed Optimization

#### Priority-Based Material Allocation
```python
def optimize_order_fulfillment():
    priority_matrix = {
        'High': {'steel_allocation': 1.0, 'lead_time_buffer': 0.5},
        'Medium': {'steel_allocation': 0.8, 'lead_time_buffer': 1.0},
        'Low': {'steel_allocation': 0.6, 'lead_time_buffer': 1.5}
    }
    
    for job in active_jobs:
        priority = job.priorityStatus
        allocate_materials(job, priority_matrix[priority])
        
    return optimized_fulfillment_schedule
```

## Material-Specific Staging Logic

### Steel Coils Staging
- **Location**: Primary staging area (closest to fabrication)
- **Inventory Target**: 4-week rolling consumption
- **Quality Requirements**: Mill certification tracking
- **Handling**: Crane-accessible positions by grade/specification

### Welding Consumables Staging  
- **Location**: Climate-controlled warehouse (moisture protection)
- **Inventory Target**: 6-week rolling consumption
- **Quality Requirements**: Batch tracking and expiration monitoring
- **Handling**: First-in-first-out rotation system

### Coating Materials Staging
- **Location**: Hazmat-compliant storage area
- **Inventory Target**: 2-week rolling consumption
- **Quality Requirements**: Temperature and humidity control
- **Handling**: Automated dispensing system integration

## Integration Points with ERP System

### Real-Time Data Feeds Required
1. **Current Inventory Levels** → Material availability calculations
2. **Active Job Status** → Demand forecasting inputs
3. **Production Cycle Timing** → Material consumption rate calculations
4. **Supplier Performance Data** → Lead time reliability factors

### Automated Decision Points
1. **Procurement Trigger Points** → Automatic PO generation
2. **Staging Instructions** → Material movement orders
3. **Quality Hold Notifications** → Alternative material sourcing
4. **Expedite Alerts** → Rush order processing

## Risk Mitigation Strategies

### Supply Chain Disruption Scenarios
1. **Primary Supplier Failure**
   - Secondary supplier activation (within 24 hours)
   - Emergency inventory deployment
   - Production schedule adjustment

2. **Transportation Delays**
   - Alternative shipping route activation
   - Local supplier emergency sourcing
   - Production priority resequencing

3. **Quality Issues**
   - Batch isolation procedures
   - Alternative grade substitution logic
   - Customer notification protocols

This logic framework provides the foundation for implementing an AI-driven supply chain forecasting system that can prevent shortages, reduce overstock, and improve order fulfillment speed through predictive material management.
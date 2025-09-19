#!/usr/bin/env python3
"""
Backend API Test Suite for User Trust & Experience Dashboard
Tests all API endpoints with realistic data scenarios
"""

import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class DashboardAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = {}
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        self.test_results[test_name] = {
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_health_check(self):
        """Test GET /api/ - Basic health check"""
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Dashboard API" in data["message"]:
                    self.log_test("Health Check", True, "API is responding correctly", data)
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected response format: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_data_generation(self):
        """Test POST /api/generate-data - Generate realistic sample data"""
        try:
            # Test with realistic parameters for e-commerce dashboard
            payload = {
                "num_users": 500,
                "num_sellers": 100,
                "num_orders": 2000,
                "num_reviews": 1200,
                "num_disputes": 100,
                "seed": 42
            }
            
            response = self.session.post(f"{API_BASE}/generate-data", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if "message" in data and "stats" in data:
                    stats = data["stats"]
                    expected_keys = ["users", "sellers", "orders", "reviews", "disputes"]
                    
                    if all(key in stats for key in expected_keys):
                        # Validate data counts match request
                        if (stats["users"] == payload["num_users"] and 
                            stats["sellers"] == payload["num_sellers"] and
                            stats["orders"] == payload["num_orders"]):
                            
                            self.log_test("Data Generation", True, 
                                        f"Generated {stats['users']} users, {stats['sellers']} sellers, "
                                        f"{stats['orders']} orders, {stats['reviews']} reviews, "
                                        f"{stats['disputes']} disputes", data)
                            return True
                        else:
                            self.log_test("Data Generation", False, 
                                        f"Data counts don't match request: {stats}")
                            return False
                    else:
                        self.log_test("Data Generation", False, 
                                    f"Missing required stats keys: {stats}")
                        return False
                else:
                    self.log_test("Data Generation", False, 
                                f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("Data Generation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Data Generation", False, f"Error: {str(e)}")
            return False
    
    def test_trust_metrics(self):
        """Test GET /api/trust-metrics - Trust metrics calculation"""
        try:
            response = self.session.get(f"{API_BASE}/trust-metrics")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate trust metrics structure
                expected_metrics = [
                    "trust_index", "dispute_rate", "refund_ratio", 
                    "policy_breach_rate", "repeat_purchase_uplift",
                    "user_satisfaction_avg", "fraud_detection_rate", 
                    "seller_performance_avg"
                ]
                
                if all(metric in data for metric in expected_metrics):
                    # Validate metric values are reasonable
                    if (0 <= data["trust_index"] <= 100 and
                        0 <= data["dispute_rate"] <= 100 and
                        0 <= data["user_satisfaction_avg"] <= 100):
                        
                        self.log_test("Trust Metrics", True, 
                                    f"Trust Index: {data['trust_index']}, "
                                    f"Dispute Rate: {data['dispute_rate']}%, "
                                    f"User Satisfaction: {data['user_satisfaction_avg']}%", data)
                        return True
                    else:
                        self.log_test("Trust Metrics", False, 
                                    f"Metric values out of expected range: {data}")
                        return False
                else:
                    self.log_test("Trust Metrics", False, 
                                f"Missing required metrics: {list(data.keys())}")
                    return False
            else:
                self.log_test("Trust Metrics", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Trust Metrics", False, f"Error: {str(e)}")
            return False
    
    def test_dashboard_stats(self):
        """Test GET /api/dashboard-stats - Key dashboard statistics"""
        try:
            response = self.session.get(f"{API_BASE}/dashboard-stats")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate dashboard stats structure
                if ("trust_metrics" in data and "totals" in data and 
                    "recent_activity" in data):
                    
                    totals = data["totals"]
                    recent = data["recent_activity"]
                    
                    # Check totals structure
                    expected_totals = ["users", "sellers", "orders", "reviews", "disputes"]
                    if all(key in totals for key in expected_totals):
                        
                        # Check recent activity structure
                        if "orders_30d" in recent and "disputes_30d" in recent:
                            self.log_test("Dashboard Stats", True, 
                                        f"Total Orders: {totals['orders']}, "
                                        f"Recent Orders (30d): {recent['orders_30d']}, "
                                        f"Recent Disputes (30d): {recent['disputes_30d']}", data)
                            return True
                        else:
                            self.log_test("Dashboard Stats", False, 
                                        f"Missing recent activity data: {recent}")
                            return False
                    else:
                        self.log_test("Dashboard Stats", False, 
                                    f"Missing totals data: {totals}")
                        return False
                else:
                    self.log_test("Dashboard Stats", False, 
                                f"Invalid response structure: {list(data.keys())}")
                    return False
            else:
                self.log_test("Dashboard Stats", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Stats", False, f"Error: {str(e)}")
            return False
    
    def test_sellers_performance(self):
        """Test GET /api/sellers-performance - Top performing sellers"""
        try:
            response = self.session.get(f"{API_BASE}/sellers-performance?limit=20")
            
            if response.status_code == 200:
                data = response.json()
                
                if "sellers" in data and isinstance(data["sellers"], list):
                    sellers = data["sellers"]
                    
                    if len(sellers) > 0:
                        # Validate seller data structure
                        first_seller = sellers[0]
                        expected_fields = ["id", "name", "trust_index", "fulfillment_rate", 
                                         "return_rate", "complaint_ratio", "category"]
                        
                        if all(field in first_seller for field in expected_fields):
                            # Check if sellers are sorted by trust_index (descending)
                            trust_scores = [s["trust_index"] for s in sellers]
                            is_sorted = all(trust_scores[i] >= trust_scores[i+1] 
                                          for i in range(len(trust_scores)-1))
                            
                            if is_sorted:
                                self.log_test("Sellers Performance", True, 
                                            f"Retrieved {len(sellers)} sellers, "
                                            f"Top seller trust index: {sellers[0]['trust_index']}", 
                                            {"seller_count": len(sellers), "top_seller": sellers[0]})
                                return True
                            else:
                                self.log_test("Sellers Performance", False, 
                                            "Sellers not properly sorted by trust index")
                                return False
                        else:
                            self.log_test("Sellers Performance", False, 
                                        f"Missing seller fields: {list(first_seller.keys())}")
                            return False
                    else:
                        self.log_test("Sellers Performance", False, "No sellers returned")
                        return False
                else:
                    self.log_test("Sellers Performance", False, 
                                f"Invalid response structure: {list(data.keys())}")
                    return False
            else:
                self.log_test("Sellers Performance", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Sellers Performance", False, f"Error: {str(e)}")
            return False
    
    def test_category_analysis(self):
        """Test GET /api/category-analysis - Performance analysis by category"""
        try:
            response = self.session.get(f"{API_BASE}/category-analysis")
            
            if response.status_code == 200:
                data = response.json()
                
                if "categories" in data and isinstance(data["categories"], list):
                    categories = data["categories"]
                    
                    if len(categories) > 0:
                        # Validate category data structure
                        first_category = categories[0]
                        expected_fields = ["_id", "avg_dispute_rate", "avg_fulfillment_rate", 
                                         "avg_trust_index", "total_sellers"]
                        
                        if all(field in first_category for field in expected_fields):
                            # Validate aggregation results are reasonable
                            if (0 <= first_category["avg_trust_index"] <= 100 and
                                first_category["total_sellers"] > 0):
                                
                                self.log_test("Category Analysis", True, 
                                            f"Analyzed {len(categories)} categories, "
                                            f"Top category: {first_category['_id']} "
                                            f"(Trust: {first_category['avg_trust_index']:.2f})", 
                                            {"category_count": len(categories), "top_category": first_category})
                                return True
                            else:
                                self.log_test("Category Analysis", False, 
                                            f"Invalid aggregation values: {first_category}")
                                return False
                        else:
                            self.log_test("Category Analysis", False, 
                                        f"Missing category fields: {list(first_category.keys())}")
                            return False
                    else:
                        self.log_test("Category Analysis", False, "No categories returned")
                        return False
                else:
                    self.log_test("Category Analysis", False, 
                                f"Invalid response structure: {list(data.keys())}")
                    return False
            else:
                self.log_test("Category Analysis", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Category Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_regional_analysis(self):
        """Test GET /api/regional-analysis - Regional user satisfaction analysis"""
        try:
            response = self.session.get(f"{API_BASE}/regional-analysis")
            
            if response.status_code == 200:
                data = response.json()
                
                if "regions" in data and isinstance(data["regions"], list):
                    regions = data["regions"]
                    
                    if len(regions) > 0:
                        # Validate region data structure
                        first_region = regions[0]
                        expected_fields = ["_id", "avg_satisfaction", "total_users", "avg_orders"]
                        
                        if all(field in first_region for field in expected_fields):
                            # Validate satisfaction scores are reasonable
                            if (1 <= first_region["avg_satisfaction"] <= 5 and
                                first_region["total_users"] > 0):
                                
                                self.log_test("Regional Analysis", True, 
                                            f"Analyzed {len(regions)} regions, "
                                            f"Top region: {first_region['_id']} "
                                            f"(Satisfaction: {first_region['avg_satisfaction']:.2f})", 
                                            {"region_count": len(regions), "top_region": first_region})
                                return True
                            else:
                                self.log_test("Regional Analysis", False, 
                                            f"Invalid satisfaction values: {first_region}")
                                return False
                        else:
                            self.log_test("Regional Analysis", False, 
                                        f"Missing region fields: {list(first_region.keys())}")
                            return False
                    else:
                        self.log_test("Regional Analysis", False, "No regions returned")
                        return False
                else:
                    self.log_test("Regional Analysis", False, 
                                f"Invalid response structure: {list(data.keys())}")
                    return False
            else:
                self.log_test("Regional Analysis", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Regional Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_dispute_trends(self):
        """Test GET /api/dispute-trends - Dispute trends over time"""
        try:
            response = self.session.get(f"{API_BASE}/dispute-trends")
            
            if response.status_code == 200:
                data = response.json()
                
                if "trends" in data and isinstance(data["trends"], list):
                    trends = data["trends"]
                    
                    if len(trends) > 0:
                        # Validate trend data structure
                        first_trend = trends[0]
                        expected_fields = ["_id", "count", "total_amount"]
                        
                        if all(field in first_trend for field in expected_fields):
                            # Validate _id structure (should have year, month, type)
                            if ("year" in first_trend["_id"] and 
                                "month" in first_trend["_id"] and
                                "type" in first_trend["_id"]):
                                
                                self.log_test("Dispute Trends", True, 
                                            f"Retrieved {len(trends)} trend data points, "
                                            f"Sample: {first_trend['_id']['type']} "
                                            f"({first_trend['_id']['year']}-{first_trend['_id']['month']}): "
                                            f"{first_trend['count']} disputes", 
                                            {"trend_count": len(trends), "sample_trend": first_trend})
                                return True
                            else:
                                self.log_test("Dispute Trends", False, 
                                            f"Invalid _id structure: {first_trend['_id']}")
                                return False
                        else:
                            self.log_test("Dispute Trends", False, 
                                        f"Missing trend fields: {list(first_trend.keys())}")
                            return False
                    else:
                        self.log_test("Dispute Trends", False, "No trends returned")
                        return False
                else:
                    self.log_test("Dispute Trends", False, 
                                f"Invalid response structure: {list(data.keys())}")
                    return False
            else:
                self.log_test("Dispute Trends", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Dispute Trends", False, f"Error: {str(e)}")
            return False
    
    def test_policy_simulation(self):
        """Test GET /api/policy-simulation - Policy impact simulation"""
        try:
            # Test with different policy scenarios
            scenarios = [
                {
                    "name": "Strict Policy",
                    "params": {"min_fulfillment_rate": 0.95, "max_complaint_ratio": 0.05, "min_trust_index": 80}
                },
                {
                    "name": "Moderate Policy", 
                    "params": {"min_fulfillment_rate": 0.85, "max_complaint_ratio": 0.10, "min_trust_index": 70}
                },
                {
                    "name": "Lenient Policy",
                    "params": {"min_fulfillment_rate": 0.75, "max_complaint_ratio": 0.15, "min_trust_index": 60}
                }
            ]
            
            all_passed = True
            scenario_results = []
            
            for scenario in scenarios:
                params = scenario["params"]
                response = self.session.get(f"{API_BASE}/policy-simulation", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate policy simulation structure
                    if ("policy_parameters" in data and "impact_analysis" in data and 
                        "recommendations" in data):
                        
                        impact = data["impact_analysis"]
                        expected_impact_fields = ["total_sellers", "compliant_sellers", 
                                                "non_compliant_sellers", "compliance_rate"]
                        
                        if all(field in impact for field in expected_impact_fields):
                            # Validate calculations
                            total = impact["total_sellers"]
                            compliant = impact["compliant_sellers"]
                            non_compliant = impact["non_compliant_sellers"]
                            
                            if total == compliant + non_compliant:
                                scenario_results.append({
                                    "scenario": scenario["name"],
                                    "compliance_rate": impact["compliance_rate"],
                                    "affected_sellers": non_compliant
                                })
                            else:
                                self.log_test(f"Policy Simulation - {scenario['name']}", False, 
                                            f"Invalid calculation: {total} != {compliant} + {non_compliant}")
                                all_passed = False
                        else:
                            self.log_test(f"Policy Simulation - {scenario['name']}", False, 
                                        f"Missing impact fields: {list(impact.keys())}")
                            all_passed = False
                    else:
                        self.log_test(f"Policy Simulation - {scenario['name']}", False, 
                                    f"Invalid response structure: {list(data.keys())}")
                        all_passed = False
                else:
                    self.log_test(f"Policy Simulation - {scenario['name']}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    all_passed = False
            
            if all_passed:
                self.log_test("Policy Simulation", True, 
                            f"All {len(scenarios)} scenarios tested successfully. "
                            f"Compliance rates: {[r['compliance_rate'] for r in scenario_results]}%", 
                            scenario_results)
                return True
            else:
                return False
                
        except Exception as e:
            self.log_test("Policy Simulation", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("=" * 80)
        print("🚀 Starting User Trust & Experience Dashboard API Tests")
        print("=" * 80)
        
        # Test sequence: Health check -> Data generation -> All analytics endpoints
        tests = [
            ("Health Check", self.test_health_check),
            ("Data Generation", self.test_data_generation),
            ("Trust Metrics", self.test_trust_metrics),
            ("Dashboard Stats", self.test_dashboard_stats),
            ("Sellers Performance", self.test_sellers_performance),
            ("Category Analysis", self.test_category_analysis),
            ("Regional Analysis", self.test_regional_analysis),
            ("Dispute Trends", self.test_dispute_trends),
            ("Policy Simulation", self.test_policy_simulation)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            if test_func():
                passed += 1
            else:
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if not result['success']:
                    print(f"  ❌ {test_name}: {result['message']}")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    print(f"🌐 Testing backend at: {API_BASE}")
    tester = DashboardAPITester()
    passed, failed, results = tester.run_all_tests()
    
    # Save detailed results to file
    with open('/app/test_results_detailed.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/test_results_detailed.json")
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)
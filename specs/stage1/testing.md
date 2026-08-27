# Stage 1: Testing Strategy

## Testing Pyramid
```
        ┌─────────────────┐
        │   E2E Tests     │
        │  (Cypress)      │
        └─────────────────┘
               ▲
        ┌─────────────────┐
        │ Integration     │
        │   (API calls)   │
        └─────────────────┘
               ▲
        ┌─────────────────┐
        │ Unit Tests      │
        │ (pytest, jest)  │
        └─────────────────┘
```

## Test Suites

### Backend Tests (Python/pytest)

#### Unit Tests
File: `api/tests/test_models.py`
```python
def test_merchant_model():
    merchant = Merchant(
        merchant_key="test123",
        name="Test Merchant"
    )
    assert merchant.merchant_key == "test123"

def test_session_amount():
    session = Session(
        merchant_key="test123",
        amount=1500000,  # Rials
        status="paid"
    )
    assert session.amount > 0
```

#### API Tests
File: `api/tests/test_endpoints.py`
```python
def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_merchants(client):
    response = client.get("/api/merchants")
    assert response.status_code == 200
    assert "merchants" in response.json()

def test_merchant_analytics(client):
    response = client.get("/api/analytics/merchant/test123")
    assert response.status_code in [200, 404]
```

### Frontend Tests (Jest + React Testing Library)

#### Component Tests
File: `next-app/components/__tests__/MerchantSelector.test.tsx`
```typescript
test('renders merchant selector', () => {
  render(<MerchantSelector merchants={testMerchants} />);
  expect(screen.getByText('Select Merchant')).toBeInTheDocument();
});

test('handles null merchants safely', () => {
  render(<MerchantSelector merchants={null} />);
  // Should not crash - null-safety pattern
});
```

### End-to-End Tests (Cypress)

#### Dashboard Flow
File: `e2e/dashboard.cy.ts`
```typescript
describe('Dashboard Overview', () => {
  it('loads analytics data', () => {
    cy.visit('/');
    cy.get('[data-testid="revenue"]').should('be.visible');
    cy.get('[data-testid="transactions"]').should('be.visible');
  });

  it('filters by merchant', () => {
    cy.visit('/');
    cy.get('[data-testid="merchant-selector"]').select('Test Merchant');
    cy.get('[data-testid="chart"]').should('be.visible');
  });
});
```

## CI/CD Pipeline

### GitHub Actions Workflow
File: `.github/workflows/test.yml`
```yaml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install backend deps
        run: |
          cd api
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run backend tests
        run: |
          cd api
          pytest tests/
          
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          
      - name: Install frontend deps
        run: |
          cd next-app
          npm ci
      
      - name: Run frontend tests
        run: |
          cd next-app
          npm test -- --passWithNoTests
```

## Test Data

### Fixtures
File: `api/tests/fixtures/sample_data.json`
```json
{
  "merchants": [
    {"merchant_key": "key1", "name": "Merchant 1"},
    {"merchant_key": "key2", "name": "Merchant 2"}
  ],
  "sessions": [
    {"id": "uuid1", "merchant_key": "key1", "session_status": "paid", "amount": 1000000},
    {"id": "uuid2", "merchant_key": "key2", "session_status": "paid", "amount": 2500000}
  ]
}
```

## Validation Checklist
- [ ] Health check endpoint responds
- [ ] API returns JSON in specified format
- [ ] Amounts are in Rials (IRR)
- [ ] Merchant data is properly linked
- [ ] Date filtering works correctly
- [ ] Null-safety in frontend components
- [ ] E2E tests pass for main dashboard views

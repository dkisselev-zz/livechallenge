# MCP Server Exploration Report

## Server Information
- **URL**: `https://vipfapwm3x.us-east-1.awsapprunner.com/mcp`
- **Server Name**: `order-mcp`
- **Version**: `1.22.0`
- **Protocol Version**: `2024-11-05`

## Communication Protocol

The server supports two communication modes:

### 1. Server-Sent Events (SSE) Mode
- **Endpoint**: `GET /mcp`
- **Required Header**: `Accept: text/event-stream`
- **Response**: Opens a persistent SSE connection
- **Use Case**: For bidirectional streaming communication

### 2. JSON-RPC POST Mode
- **Endpoint**: `POST /mcp`
- **Required Headers**: 
  - `Content-Type: application/json`
  - `Accept: application/json`
- **Protocol**: JSON-RPC 2.0
- **Use Case**: Standard request/response pattern

## Server Capabilities

The server supports:
- ✅ **Tools**: 8 tools available
- ✅ **Resources**: None (empty list)
- ✅ **Prompts**: None (empty list)
- ✅ **Experimental**: Supported

## Available Tools

### 1. `list_products`
**Description**: List products with optional filters.

**Parameters**:
- `category` (string, optional): Filter by category (e.g., "Computers", "Monitors")
- `is_active` (boolean, optional): Filter by active status

**Returns**: Formatted string with products, one per line

**Use Cases**:
- Browse inventory by category
- Check stock levels
- Find available products

**Example Response**: Returns 200 products across categories (Computers, Monitors, Printers, Accessories, Networking)

---

### 2. `get_product`
**Description**: Get detailed product information by SKU.

**Parameters**:
- `sku` (string, required): Product SKU (e.g., "COM-0001")

**Returns**: Formatted product details including:
- Product name
- SKU
- Category
- Price
- Stock level
- Status
- Description

**Raises**: `ProductNotFoundError` if SKU doesn't exist

**Use Cases**:
- Get current price
- Check inventory for specific item
- Verify product details before ordering

---

### 3. `search_products`
**Description**: Search products by name or description.

**Parameters**:
- `query` (string, required): Search term (case-insensitive, partial match)

**Returns**: Formatted search results (same format as list_products)

**Use Cases**:
- Find products by keyword
- Help customers discover items
- Natural language product lookup

**Example**: Searching for "monitor" returns 40 matching products

---

### 4. `get_customer`
**Description**: Get customer information by ID.

**Parameters**:
- `customer_id` (string, required): Customer UUID

**Returns**: Formatted customer details

**Raises**: `CustomerNotFoundError` if customer doesn't exist

**Use Cases**:
- Look up customer details
- Verify shipping address
- Check customer role/permissions

---

### 5. `verify_customer_pin`
**Description**: Verify customer identity with email and PIN.

**Parameters**:
- `email` (string, required): Customer email address
- `pin` (string, required): 4-digit PIN code

**Returns**: Formatted customer details if verified

**Raises**: `CustomerNotFoundError` if email not found or PIN incorrect

**Use Cases**:
- Authenticate customer before order placement
- Verify identity for account access
- Simple security check

---

### 6. `list_orders`
**Description**: List orders with optional filters.

**Parameters**:
- `customer_id` (string, optional): Filter by customer UUID
- `status` (string, optional): Filter by status (draft|submitted|approved|fulfilled|cancelled)

**Returns**: Formatted order list

**Use Cases**:
- View customer order history
- Track pending orders
- Analyze order patterns (autonomous agents)
- Find orders by status

---

### 7. `get_order`
**Description**: Get detailed order information including items.

**Parameters**:
- `order_id` (string, required): Order UUID

**Returns**: Formatted order with line items

**Raises**: `OrderNotFoundError` if order doesn't exist

**Use Cases**:
- View order details
- Check order contents
- Analyze what products are ordered together (cross-sell analysis)

---

### 8. `create_order`
**Description**: Create a new order with items.

**Parameters**:
- `customer_id` (string, required): Customer UUID
- `items` (array, required): List of items, each with:
  - `sku` (string): Product SKU (e.g., "MON-0054")
  - `quantity` (int): Must be > 0
  - `unit_price` (string): Decimal as string
  - `currency` (string): Default "USD"

**Returns**: Formatted order confirmation

**Raises**:
- `CustomerNotFoundError`: If customer doesn't exist
- `ProductNotFoundError`: If any product SKU doesn't exist
- `InsufficientInventoryError`: If quantity exceeds available stock

**Use Cases**:
- Place new orders for customers
- Automatically decrements inventory (atomic)
- Validates all constraints before committing

**Note**: Order starts in "submitted" status with "pending" payment

---

## Product Categories

The server manages products across 5 main categories:
1. **Computers** (COM-*): Desktops, Laptops, Gaming PCs, MacBooks, etc.
2. **Monitors** (MON-*): Various sizes and types (24", 27", 32", 4K, Ultrawide, etc.)
3. **Printers** (PRI-*): Laser, Inkjet, 3D, Large Format, etc.
4. **Accessories** (ACC-*): Keyboards, Mice, Webcams, Headsets, USB Hubs, etc.
5. **Networking** (NET-*): Routers, Switches, Access Points, Modems

**Total Products**: 200+ products in inventory

---

## Example Usage

### Initialize Connection
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "test-client",
      "version": "1.0.0"
    }
  }
}
```

### List Tools
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

### Call a Tool
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_product",
    "arguments": {
      "sku": "COM-0001"
    }
  }
}
```

---

## Error Handling

The server returns proper JSON-RPC 2.0 error responses:
- **406 Not Acceptable**: When incorrect `Accept` header is used
- **ProductNotFoundError**: When product SKU doesn't exist
- **CustomerNotFoundError**: When customer doesn't exist or PIN is incorrect
- **OrderNotFoundError**: When order doesn't exist
- **InsufficientInventoryError**: When order quantity exceeds stock

---

## Testing Results

✅ Successfully initialized connection
✅ Listed all 8 available tools
✅ Tested `list_products` - Returns 200 products
✅ Tested `get_product` - Successfully retrieved product details
✅ Tested `search_products` - Successfully found 40 monitors
✅ Verified JSON-RPC 2.0 compliance
✅ Verified proper error handling

---

## Notes

- The server requires proper `Accept` headers:
  - Use `Accept: text/event-stream` for SSE connections
  - Use `Accept: application/json` for JSON-RPC POST requests
- All tool responses include both `content` (formatted text) and `structuredContent` (structured data)
- The server appears to be a complete order management system with product catalog, customer management, and order processing capabilities


# Zepto MCP integration

The Household Agent can turn a discovered recipe's deterministic ingredient gaps
into a Zepto cart. The user must connect a Zepto account through the official
OAuth phone-and-OTP flow first. The app stores only a Fernet-encrypted access
token in the local SQLite database, scoped to that household.

## Included flow

1. `GET /api/households/{id}/zepto/status` reports connection state.
2. `POST /api/households/{id}/zepto/connect` starts OAuth with PKCE.
3. `GET /api/zepto/callback` exchanges the authorization code and persists the
   encrypted token.
4. `POST /api/households/{id}/zepto/cart` searches Zepto MCP product inventory
   for each missing ingredient, adds in-stock matches to the authenticated cart,
   returns prices/totals/checkout URLs, and records `zepto_cart_created` in the
   audit timeline.
5. The user completes payment in Zepto. Cart creation never calls order
   placement. After delivery, `POST /api/households/{id}/zepto/sync-inventory`
   adds the confirmed purchased ingredients to local inventory with shelf-life
   estimates.

## Setup

Use the `HOUSEHOLD_ZEPTO_*` values in `.env.example`. The official Zepto MCP
uses OAuth with an Indian mobile number and OTP. Its allowed redirect URIs must
include this app's callback; request allow-listing from Zepto if necessary.
Do not enable `HOUSEHOLD_ZEPTO_MOCK_ENABLED` outside local tests/demos.

## Notes

The provider speaks MCP Streamable HTTP JSON-RPC and calls the official
`search_products` and `cart_management` tools. It also exposes a
`create_order_payment` wrapper for an explicit future payment-confirmation
screen, but the current cart route deliberately does not invoke it because
Zepto documents order placement as a real, non-sandbox transaction.

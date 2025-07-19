# API Reference

## REST API

Run the server:

```bash
FLASK_APP=api/server.py flask run --port=5000
```

**Create an item**

```bash
curl -X POST http://localhost:5000/items \
     -H "Content-Type: application/json" \
     -d '{"name":"Padron 1964","category":"Cigar","quantity":2}'
```

**Get an item**

```bash
curl http://localhost:5000/items/1
```

**Search items**

```bash
curl http://localhost:5000/items/search?keyword=padron
```

**Filter by category**

```bash
curl http://localhost:5000/items/filter?category=Cigar
```

**Category distribution**

```bash
curl http://localhost:5000/analytics/category
```

**Time distribution**

```bash
curl http://localhost:5000/analytics/time
```


## GraphQL API

Open the GraphiQL playground:

```
http://localhost:5000/graphql
```

**Query an item**

```graphql
query {
  getItem(id:"1") {
    id
    name
    quantity
  }
}
```

**Create an item**

```graphql
mutation {
  createItem(name:"Montecristo",category:"Cigar",quantity:3) {
    id
    name
  }
}
```

**Analytics**

```graphql
query {
  categoryDistribution { category count }
  timeDistribution     { period   count }
}
```
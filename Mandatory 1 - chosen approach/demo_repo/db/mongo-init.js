db.createCollection("tickets")
db.tickets.insertMany([
  {
    "name": "Meal Ticket",
    "description": "A meal ticket for a specific event.",
    "price": 10.99,
    "quantity": 50,
    "createdAt": new Date(),
    "updatedAt": new Date()
  }
])

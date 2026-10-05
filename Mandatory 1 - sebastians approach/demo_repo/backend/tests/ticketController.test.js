const request = require('supertest');
const app = require('../app');

describe('Ticket Controller', () => {
  it('should create a new ticket', async () => {
    const response = await request(app)
      .post('/api/tickets')
      .send({
        name: 'Meal Ticket',
        description: 'A meal ticket for a specific event.',
        price: 10.99,
        quantity: 50
      });

    expect(response.status).toBe(201);
    expect(response.body.name).toBe('Meal Ticket');
  });

  it('should get all tickets', async () => {
    const response = await request(app)
      .get('/api/tickets');

    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
  });

  it('should update a ticket', async () => {
    const createResponse = await request(app)
      .post('/api/tickets')
      .send({
        name: 'Meal Ticket',
        description: 'A meal ticket for a specific event.',
        price: 10.99,
        quantity: 50
      });

    const updateResponse = await request(app)
      .put(`/api/tickets/${createResponse.body._id}`)
      .send({
        name: 'Updated Meal Ticket',
        description: 'An updated meal ticket for a specific event.',
        price: 12.99,
        quantity: 40
      });

    expect(updateResponse.status).toBe(200);
    expect(updateResponse.body.name).toBe('Updated Meal Ticket');
  });

  it('should delete a ticket', async () => {
    const createResponse = await request(app)
      .post('/api/tickets')
      .send({
        name: 'Meal Ticket',
        description: 'A meal ticket for a specific event.',
        price: 10.99,
        quantity: 50
      });

    const deleteResponse = await request(app)
      .delete(`/api/tickets/${createResponse.body._id}`);

    expect(deleteResponse.status).toBe(200);
    expect(deleteResponse.body.message).toBe('Ticket deleted successfully.');
  });
});

import React from 'react';
import { render, screen } from '@testing-library/react';
import axios from 'axios';
import TicketApp from '../src/TicketApp';

jest.mock('axios');

describe('TicketApp', () => {
  it('renders the app and creates a new ticket', async () => {
    axios.post.mockResolvedValue({ data: { _id: '123', name: 'Meal Ticket', description: 'A meal ticket for a specific event.', price: 10.99, quantity: 50 } });
    render(<TicketApp />);
    const input = screen.getByPlaceholderText('Name');
    input.value = 'Meal Ticket';
    fireEvent.change(input);
    fireEvent.submit(screen.getByText('Create Ticket'));
    expect(axios.post).toHaveBeenCalledWith('http://localhost:5000/api/tickets', { name: 'Meal Ticket', description: '', price: '', quantity: '' });
  });

  it('renders the app and updates a ticket', async () => {
    axios.put.mockResolvedValue({ data: { _id: '123', name: 'Updated Meal Ticket', description: 'An updated meal ticket for a specific event.', price: 12.99, quantity: 40 } });
    render(<TicketApp />);
    fireEvent.click(screen.getByText('Increment'));
    expect(axios.put).toHaveBeenCalledWith('http://localhost:5000/api/tickets/123', { _id: '123', name: 'Meal Ticket', description: '', price: '', quantity: 51 });
  });

  it('renders the app and deletes a ticket', async () => {
    axios.delete.mockResolvedValue({});
    render(<TicketApp />);
    fireEvent.click(screen.getByText('Delete'));
    expect(axios.delete).toHaveBeenCalledWith('http://localhost:5000/api/tickets/123');
  });
});

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TicketApp = () => {
  const [tickets, setTickets] = useState([]);
  const [newTicket, setNewTicket] = useState({ name: '', description: '', price: '', quantity: '' });

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/tickets');
      setTickets(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const createTicket = async () => {
    try {
      await axios.post('http://localhost:5000/api/tickets', newTicket);
      fetchTickets();
      setNewTicket({ name: '', description: '', price: '', quantity: '' });
    } catch (error) {
      console.error(error);
    }
  };

  const updateTicket = async (id, updatedTicket) => {
    try {
      await axios.put(`http://localhost:5000/api/tickets/${id}`, updatedTicket);
      fetchTickets();
    } catch (error) {
      console.error(error);
    }
  };

  const deleteTicket = async (id) => {
    try {
      await axios.delete(`http://localhost:5000/api/tickets/${id}`);
      fetchTickets();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div>
      <h1>Meal Tickets</h1>
      <form onSubmit={(e) => { e.preventDefault(); createTicket(); }}>
        <input
          type="text"
          value={newTicket.name}
          onChange={(e) => setNewTicket({ ...newTicket, name: e.target.value })}
          placeholder="Name"
        />
        <input
          type="text"
          value={newTicket.description}
          onChange={(e) => setNewTicket({ ...newTicket, description: e.target.value })}
          placeholder="Description"
        />
        <input
          type="number"
          value={newTicket.price}
          onChange={(e) => setNewTicket({ ...newTicket, price: e.target.value })}
          placeholder="Price"
        />
        <input
          type="number"
          value={newTicket.quantity}
          onChange={(e) => setNewTicket({ ...newTicket, quantity: e.target.value })}
          placeholder="Quantity"
        />
        <button type="submit">Create Ticket</button>
      </form>
      <ul>
        {tickets.map((ticket) => (
          <li key={ticket._id}>
            {ticket.name} - {ticket.description} - ${ticket.price} - {ticket.quantity}
            <button onClick={() => updateTicket(ticket._id, { ...ticket, quantity: ticket.quantity + 1 })}>Increment</button>
            <button onClick={() => deleteTicket(ticket._id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TicketApp;

const mongoose = require('mongoose');
const Ticket = mongoose.model('Ticket');

exports.createTicket = async (req, res) => {
  const ticket = new Ticket(req.body);
  await ticket.save();
  res.status(201).json(ticket);
};

exports.getTickets = async (req, res) => {
  const tickets = await Ticket.find();
  res.json(tickets);
};

exports.updateTicket = async (req, res) => {
  const updatedTicket = await Ticket.findByIdAndUpdate(req.params.id, req.body, { new: true });
  res.json(updatedTicket);
};

exports.deleteTicket = async (req, res) => {
  await Ticket.findByIdAndDelete(req.params.id);
  res.status(204).send();
};

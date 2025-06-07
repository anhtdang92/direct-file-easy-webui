import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App Component', () => {
  it('renders the header with correct title', () => {
    render(<App />);
    const headerElement = screen.getByText('AI Tax Filer');
    expect(headerElement).toBeInTheDocument();
  });

  it('renders the welcome message', () => {
    render(<App />);
    const welcomeElement = screen.getByText('Welcome to AI Tax Filer');
    expect(welcomeElement).toBeInTheDocument();
  });
}); 
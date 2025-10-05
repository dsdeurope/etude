import { render, screen } from '@testing-library/react';
import App from './App';

// Micro-test 1: L'app se rend sans crash
test('renders without crashing', () => {
  render(<App />);
});

// Micro-test 2: Le titre principal s'affiche
test('renders main title', () => {
  render(<App />);
  const titleElement = screen.getByRole('heading', { name: /📖 Bible Study AI/i });
  expect(titleElement).toBeInTheDocument();
});

// Micro-test 3: Message de succès présent
test('shows success message', () => {
  render(<App />);
  const successElement = screen.getByText(/DÉPLOIEMENT RÉUSSI/i);
  expect(successElement).toBeInTheDocument();
});

// Micro-test 4: Sélecteurs fonctionnels
test('renders selectors', () => {
  render(<App />);
  const selectors = screen.getAllByRole('combobox');
  expect(selectors).toHaveLength(2);
});

// Micro-test 5: Bouton principal présent
test('renders generate button', () => {
  render(<App />);
  const buttonElement = screen.getByText(/Générer Étude/i);
  expect(buttonElement).toBeInTheDocument();
});
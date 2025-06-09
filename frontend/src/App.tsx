import React, { useState } from 'react';

interface FormData {
  // Personal Information
  firstName: string;
  lastName: string;
  ssn: string;
  dateOfBirth: string;
  filingStatus: 'single' | 'married' | 'head' | 'widow' | 'married_separate';
  address: string;
  city: string;
  state: string;
  zip: string;
  email: string;
  phone: string;

  // Income Information (Form 1040)
  wages: number;
  interest: number;
  dividends: number;
  capitalGains: number;
  retirementIncome: number;
  socialSecurity: number;
  otherIncome: number;

  // Deductions (Schedule A)
  medicalExpenses: number;
  stateTaxes: number;
  localTaxes: number;
  propertyTaxes: number;
  mortgageInterest: number;
  charitableContributions: number;
  casualtyLosses: number;
  otherDeductions: number;

  // Credits
  childTaxCredit: number;
  educationCredits: number;
  retirementSavingsCredit: number;
  earnedIncomeCredit: number;
  otherCredits: number;

  // Business Information (Schedule C)
  business: {
    name: string;
    type: string;
    income: number;
    expenses: number;
    inventory: number;
  };

  // Investment Information (Schedule D)
  stockSales: Array<{
    description: string;
    purchaseDate: string;
    saleDate: string;
    costBasis: number;
    salePrice: number;
  }>;

  // Additional Information
  dependents: Array<{
    name: string;
    relationship: string;
    ssn: string;
    dateOfBirth: string;
  }>;
}

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<FormData>({
    firstName: '',
    lastName: '',
    ssn: '',
    dateOfBirth: '',
    filingStatus: 'single',
    address: '',
    city: '',
    state: '',
    zip: '',
    email: '',
    phone: '',
    wages: 0,
    interest: 0,
    dividends: 0,
    capitalGains: 0,
    retirementIncome: 0,
    socialSecurity: 0,
    otherIncome: 0,
    medicalExpenses: 0,
    stateTaxes: 0,
    localTaxes: 0,
    propertyTaxes: 0,
    mortgageInterest: 0,
    charitableContributions: 0,
    casualtyLosses: 0,
    otherDeductions: 0,
    childTaxCredit: 0,
    educationCredits: 0,
    retirementSavingsCredit: 0,
    earnedIncomeCredit: 0,
    otherCredits: 0,
    business: {
      name: '',
      type: '',
      income: 0,
      expenses: 0,
      inventory: 0
    },
    stockSales: [],
    dependents: []
  });

  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:3001/api/logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `Form submitted: ${JSON.stringify(formData)}`,
          level: 'info'
        }),
      });
      
      const data = await response.json();
      setMessage('Form submitted successfully!');
      console.log('Submission response:', data);
    } catch (error) {
      setMessage('Error submitting form. Please try again.');
      console.error('Submission error:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-white mb-6">Personal Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="firstName" className="block text-sm font-medium text-zinc-300">
                  First Name
                </label>
                <input
                  type="text"
                  name="firstName"
                  id="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label htmlFor="lastName" className="block text-sm font-medium text-zinc-300">
                  Last Name
                </label>
                <input
                  type="text"
                  name="lastName"
                  id="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label htmlFor="ssn" className="block text-sm font-medium text-zinc-300">
                  Social Security Number
                </label>
                <input
                  type="text"
                  name="ssn"
                  id="ssn"
                  value={formData.ssn}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label htmlFor="dateOfBirth" className="block text-sm font-medium text-zinc-300">
                  Date of Birth
                </label>
                <input
                  type="date"
                  name="dateOfBirth"
                  id="dateOfBirth"
                  value={formData.dateOfBirth}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label htmlFor="filingStatus" className="block text-sm font-medium text-zinc-300">
                  Filing Status
                </label>
                <select
                  name="filingStatus"
                  id="filingStatus"
                  value={formData.filingStatus}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                >
                  <option value="single">Single</option>
                  <option value="married">Married Filing Jointly</option>
                  <option value="head">Head of Household</option>
                  <option value="widow">Qualifying Widow(er)</option>
                  <option value="married_separate">Married Filing Separately</option>
                </select>
              </div>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-white mb-6">Income Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="wages" className="block text-sm font-medium text-zinc-300">
                  Wages, Salaries, Tips
                </label>
                <input
                  type="number"
                  name="wages"
                  id="wages"
                  value={formData.wages}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label htmlFor="interest" className="block text-sm font-medium text-zinc-300">
                  Interest Income
                </label>
                <input
                  type="number"
                  name="interest"
                  id="interest"
                  value={formData.interest}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label htmlFor="dividends" className="block text-sm font-medium text-zinc-300">
                  Dividends
                </label>
                <input
                  type="number"
                  name="dividends"
                  id="dividends"
                  value={formData.dividends}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label htmlFor="capitalGains" className="block text-sm font-medium text-zinc-300">
                  Capital Gains
                </label>
                <input
                  type="number"
                  name="capitalGains"
                  id="capitalGains"
                  value={formData.capitalGains}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
            </div>
          </div>
        );
      case 3:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-white mb-6">Deductions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="medicalExpenses" className="block text-sm font-medium text-zinc-300">
                  Medical Expenses
                </label>
                <input
                  type="number"
                  name="medicalExpenses"
                  id="medicalExpenses"
                  value={formData.medicalExpenses}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label htmlFor="stateTaxes" className="block text-sm font-medium text-zinc-300">
                  State Taxes Paid
                </label>
                <input
                  type="number"
                  name="stateTaxes"
                  id="stateTaxes"
                  value={formData.stateTaxes}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label htmlFor="mortgageInterest" className="block text-sm font-medium text-zinc-300">
                  Mortgage Interest
                </label>
                <input
                  type="number"
                  name="mortgageInterest"
                  id="mortgageInterest"
                  value={formData.mortgageInterest}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label htmlFor="charitableContributions" className="block text-sm font-medium text-zinc-300">
                  Charitable Contributions
                </label>
                <input
                  type="number"
                  name="charitableContributions"
                  id="charitableContributions"
                  value={formData.charitableContributions}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-xl bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <header className="bg-zinc-900 border-b border-zinc-800">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent tracking-tight">
            Prism
          </h1>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 shadow-xl backdrop-blur-sm">
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex space-x-2">
                    {[1, 2, 3].map((step) => (
                      <div
                        key={step}
                        className={`w-3 h-3 rounded-full ${
                          currentStep === step
                            ? 'bg-blue-500'
                            : 'bg-zinc-700'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-sm text-zinc-400">
                    Step {currentStep} of 3
                  </span>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {renderStep()}

                <div className="flex justify-between mt-8">
                  {currentStep > 1 && (
                    <button
                      type="button"
                      onClick={() => setCurrentStep(currentStep - 1)}
                      className="px-4 py-2 border border-zinc-700 rounded-xl text-sm font-medium text-white hover:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
                    >
                      Previous
                    </button>
                  )}
                  {currentStep < 3 ? (
                    <button
                      type="button"
                      onClick={() => setCurrentStep(currentStep + 1)}
                      className="ml-auto px-4 py-2 border border-transparent rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
                    >
                      Next
                    </button>
                  ) : (
                    <button
                      type="submit"
                      className="ml-auto px-4 py-2 border border-transparent rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
                    >
                      Submit
                    </button>
                  )}
                </div>
              </form>

              {message && (
                <div className="mt-4 p-4 rounded-xl bg-zinc-800 border border-zinc-700">
                  <p className="text-sm text-green-400">{message}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App; 
import React from 'react';
import { Link } from 'react-router-dom';
import { CreditCard, ExternalLink } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Payment } from '../../types';
import { formatCurrency, formatDate } from '../../lib/utils';

type PaymentsListProps = {
  payments: Payment[];
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'paid':
      return 'bg-green-100 text-green-800';
    case 'pending':
      return 'bg-yellow-100 text-yellow-800';
    case 'overdue':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const PaymentsList = ({ payments }: PaymentsListProps) => {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold flex items-center">
          <CreditCard className="mr-2 h-5 w-5 text-blue-600" />
          Recent Payments
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {payments.length > 0 ? (
            payments.map((payment) => (
              <div key={payment.id} className="flex items-center justify-between border-b border-gray-100 pb-4 last:border-0 last:pb-0">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 capitalize">{payment.type} Payment</h4>
                  <p className="text-xs text-gray-500">Due: {formatDate(payment.dueDate)}</p>
                  {payment.paidDate && (
                    <p className="text-xs text-gray-500">Paid: {formatDate(payment.paidDate)}</p>
                  )}
                </div>
                <div className="flex items-center">
                  <div className="text-right mr-2">
                    <div className="text-sm font-medium">{formatCurrency(payment.amount)}</div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(payment.status)}`}>
                      {payment.status}
                    </span>
                  </div>
                  <Link to={`/payments/${payment.id}`} className="text-blue-600 hover:text-blue-800">
                    <ExternalLink className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            ))
          ) : (
            <div className="py-6 text-center">
              <p className="text-sm text-gray-500">No payments found</p>
            </div>
          )}
        </div>
        
        {payments.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <Link 
              to="/payments" 
              className="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center"
            >
              View all payments
              <ExternalLink className="ml-1 h-3 w-3" />
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PaymentsList;
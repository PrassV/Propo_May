import React from 'react';
import { Link } from 'react-router-dom';
import { Wrench, ExternalLink } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { MaintenanceRequest } from '../../types';
import { formatDate } from '../../lib/utils';

type MaintenanceRequestListProps = {
  requests: MaintenanceRequest[];
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'low':
      return 'bg-green-100 text-green-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'high':
      return 'bg-orange-100 text-orange-800';
    case 'emergency':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'new':
      return 'bg-blue-100 text-blue-800';
    case 'in_progress':
      return 'bg-yellow-100 text-yellow-800';
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'cancelled':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const MaintenanceRequestList = ({ requests }: MaintenanceRequestListProps) => {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold flex items-center">
          <Wrench className="mr-2 h-5 w-5 text-blue-600" />
          Maintenance Requests
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {requests.length > 0 ? (
            requests.map((request) => (
              <div key={request.id} className="flex items-start border-b border-gray-100 pb-4 last:border-0 last:pb-0">
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-900">{request.title}</h4>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getPriorityColor(request.priority)}`}>
                      {request.priority}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">Unit {request.unitNumber}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <div className="text-xs text-gray-500">
                      Created: {formatDate(request.createdAt)}
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(request.status)}`}>
                      {request.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
                <Link to={`/maintenance/${request.id}`} className="ml-2 text-blue-600 hover:text-blue-800 flex-shrink-0">
                  <ExternalLink className="h-4 w-4" />
                </Link>
              </div>
            ))
          ) : (
            <div className="py-6 text-center">
              <p className="text-sm text-gray-500">No maintenance requests found</p>
            </div>
          )}
        </div>
        
        {requests.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <Link 
              to="/maintenance" 
              className="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center"
            >
              View all requests
              <ExternalLink className="ml-1 h-3 w-3" />
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default MaintenanceRequestList;
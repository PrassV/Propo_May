import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ExternalLink } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Property } from '../../types';

type PropertyListProps = {
  properties: Property[];
};

const PropertyList = ({ properties }: PropertyListProps) => {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold flex items-center">
          <Home className="mr-2 h-5 w-5 text-blue-600" />
          Properties Overview
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {properties.length > 0 ? (
            properties.map((property) => (
              <div key={property.id} className="flex items-center border-b border-gray-100 pb-4 last:border-0 last:pb-0">
                <div className="h-12 w-12 rounded-md overflow-hidden flex-shrink-0">
                  <img 
                    src={property.imageUrl} 
                    alt={property.name} 
                    className="h-full w-full object-cover"
                  />
                </div>
                <div className="ml-4 flex-1">
                  <h4 className="text-sm font-medium text-gray-900">{property.name}</h4>
                  <p className="text-xs text-gray-500">{property.address}, {property.city}</p>
                  <div className="mt-1 flex items-center text-xs">
                    <span className="text-blue-600 font-medium">{property.availableUnits}</span>
                    <span className="text-gray-500 ml-1">available units of {property.units}</span>
                  </div>
                </div>
                <Link to={`/properties/${property.id}`} className="text-blue-600 hover:text-blue-800">
                  <ExternalLink className="h-4 w-4" />
                </Link>
              </div>
            ))
          ) : (
            <div className="py-6 text-center">
              <p className="text-sm text-gray-500">No properties found</p>
            </div>
          )}
        </div>
        
        {properties.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <Link 
              to="/properties" 
              className="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center"
            >
              View all properties
              <ExternalLink className="ml-1 h-3 w-3" />
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PropertyList;
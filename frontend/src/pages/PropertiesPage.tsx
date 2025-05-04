import React from 'react';
import { Building2, Plus, Search, MapPin, Home } from 'lucide-react';
import Header from '../components/layout/Header';
import { Card, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { useApp } from '../context/AppContext';

const PropertiesPage = () => {
  const { properties, isLoading } = useApp();
  const [searchQuery, setSearchQuery] = React.useState('');
  
  const filteredProperties = properties.filter(
    (property) => 
      property.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      property.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
      property.city.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  return (
    <div className="min-h-screen">
      <Header title="Properties" />
      
      <main className="p-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
          <div className="relative flex-1 max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <Input
              type="text"
              placeholder="Search properties..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <Button className="flex items-center">
            <Plus className="h-5 w-5 mr-1" />
            Add Property
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProperties.map((property) => (
            <Card key={property.id} className="overflow-hidden hover:shadow-md transition-shadow">
              <div className="aspect-video relative">
                <img 
                  src={property.imageUrl} 
                  alt={property.name} 
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-3 right-3 bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                  {property.type}
                </div>
              </div>
              <CardContent className="p-4">
                <h3 className="text-lg font-semibold mb-1">{property.name}</h3>
                <div className="flex items-start text-gray-600 mb-3">
                  <MapPin className="h-4 w-4 flex-shrink-0 mt-0.5 mr-1" />
                  <p className="text-sm">{property.address}, {property.city}, {property.state} {property.zipCode}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-2 mb-4">
                  <div className="bg-gray-50 p-2 rounded">
                    <p className="text-xs text-gray-500">Total Units</p>
                    <p className="font-semibold">{property.units}</p>
                  </div>
                  <div className="bg-gray-50 p-2 rounded">
                    <p className="text-xs text-gray-500">Available</p>
                    <p className="font-semibold">{property.availableUnits}</p>
                  </div>
                </div>
                
                <Button variant="outline" className="w-full">View Details</Button>
              </CardContent>
            </Card>
          ))}
          
          {filteredProperties.length === 0 && (
            <div className="col-span-full flex flex-col items-center justify-center p-10 bg-gray-50 rounded-lg">
              <div className="bg-gray-100 p-3 rounded-full mb-3">
                <Building2 className="h-6 w-6 text-gray-500" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-1">No properties found</h3>
              <p className="text-gray-500 text-center mb-4">
                {searchQuery ? 'Try adjusting your search' : 'Add your first property to get started'}
              </p>
              <Button>
                <Plus className="h-5 w-5 mr-1" />
                Add Property
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default PropertiesPage;
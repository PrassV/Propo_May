import React from 'react';
import { Card, CardContent } from '../ui/Card';
import { cn } from '../../lib/utils';

type StatCardProps = {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
};

const StatCard = ({ title, value, icon, trend, className }: StatCardProps) => {
  return (
    <Card className={cn('h-full', className)}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="mt-1 text-2xl font-semibold">{value}</p>
            
            {trend && (
              <div className="mt-1 flex items-center text-sm">
                <span
                  className={cn({
                    'text-green-600': trend.isPositive,
                    'text-red-600': !trend.isPositive,
                  })}
                >
                  {trend.isPositive ? '+' : '-'}{Math.abs(trend.value)}%
                </span>
                <span className="text-gray-500 ml-1">from last month</span>
              </div>
            )}
          </div>
          
          <div className="rounded-full p-3 bg-blue-100 text-blue-600">
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default StatCard;
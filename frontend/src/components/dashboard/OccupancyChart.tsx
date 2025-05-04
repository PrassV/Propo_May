import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

type OccupancyChartProps = {
  occupied: number;
  available: number;
};

const OccupancyChart = ({ occupied, available }: OccupancyChartProps) => {
  const data = {
    labels: ['Occupied', 'Available'],
    datasets: [
      {
        data: [occupied, available],
        backgroundColor: ['#1E40AF', '#E2E8F0'],
        borderColor: ['#1E40AF', '#E2E8F0'],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    cutout: '70%',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          usePointStyle: true,
          boxWidth: 8,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const value = context.raw;
            const percentage = Math.round((value / total) * 100);
            return `${context.label}: ${value} (${percentage}%)`;
          }
        }
      }
    },
  };

  // Calculate occupancy rate
  const total = occupied + available;
  const occupancyRate = total > 0 ? Math.round((occupied / total) * 100) : 0;

  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold">Occupancy Rate</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative h-48 w-full">
          <Doughnut data={data} options={options} />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
            <div className="text-3xl font-bold text-blue-700">{occupancyRate}%</div>
            <div className="text-xs text-gray-500">Occupancy</div>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-4 text-center">
          <div>
            <div className="text-lg font-semibold">{occupied}</div>
            <div className="text-xs text-gray-500">Occupied Units</div>
          </div>
          <div>
            <div className="text-lg font-semibold">{available}</div>
            <div className="text-xs text-gray-500">Available Units</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default OccupancyChart;
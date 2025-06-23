import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, Search, Filter, Briefcase, Edit, Trash2, Copy } from 'lucide-react';

export const Jobs: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground" data-testid="page-title">
            Job Positions
          </h1>
          <p className="text-muted-foreground" data-testid="page-subtitle">
            Manage job positions and interview templates
          </p>
        </div>
        <Button className="flex items-center gap-2" data-testid="add-job-btn">
          <Plus className="h-4 w-4" />
          Add Job Position
        </Button>
      </div>

      {/* Search and Filter Bar */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search job positions..."
            className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            data-testid="search-input"
          />
        </div>
        <Button variant="outline" className="flex items-center gap-2" data-testid="filter-btn">
          <Filter className="h-4 w-4" />
          Filter by Department
        </Button>
      </div>

      {/* Job Positions List */}
      <Card>
        <CardHeader>
          <CardTitle>Job Positions</CardTitle>
          <CardDescription>
            Manage job positions and their interview question templates
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Briefcase className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">
              No job positions found. Add your first job position to get started.
            </p>
            <Button className="mt-4" data-testid="empty-state-add-btn">
              Add First Job Position
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Template Builder Section */}
      <Card>
        <CardHeader>
          <CardTitle>Interview Templates</CardTitle>
          <CardDescription>
            Build and manage question templates for each job position
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-muted-foreground">
              Create job positions to start building interview templates
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Job Positions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">All departments</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Templates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">With questions assigned</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Interviews Conducted</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">Using these templates</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg. Questions per Job</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">-</div>
            <p className="text-xs text-muted-foreground">No data</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks for job position management
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="flex items-center gap-2 h-auto p-4">
              <Plus className="h-5 w-5" />
              <div className="text-left">
                <div className="font-medium">Create Job Position</div>
                <div className="text-sm text-muted-foreground">Add a new job position</div>
              </div>
            </Button>

            <Button variant="outline" className="flex items-center gap-2 h-auto p-4" disabled>
              <Edit className="h-5 w-5" />
              <div className="text-left">
                <div className="font-medium">Build Template</div>
                <div className="text-sm text-muted-foreground">Create question template</div>
              </div>
            </Button>

            <Button variant="outline" className="flex items-center gap-2 h-auto p-4" disabled>
              <Copy className="h-5 w-5" />
              <div className="text-left">
                <div className="font-medium">Clone Template</div>
                <div className="text-sm text-muted-foreground">Copy existing template</div>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

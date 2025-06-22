import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, Plus, Search } from 'lucide-react';

export const Documents: React.FC = () => {
  const documents = [
    { id: 1, name: 'Cover page', type: 'Cover page', status: 'In Progress', target: 18, unit: 5, reviewer: 'Eddie Lake' },
    { id: 2, name: 'Table of contents', type: 'Table of contents', status: 'Done', target: 29, unit: 24, reviewer: 'Eddie Lake' },
    { id: 3, name: 'Executive summary', type: 'Narrative', status: 'Done', target: 10, unit: 13, reviewer: 'Eddie Lake' },
    { id: 4, name: 'Technical approach', type: 'Narrative', status: 'Done', target: 27, unit: 23, reviewer: 'Janik Tashpulatov' },
    { id: 5, name: 'Design', type: 'Narrative', status: 'In Progress', target: 2, unit: 18, reviewer: 'Janik Tashpulatov' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Documents</h1>
          <p className="text-muted-foreground">
            Manage and organize your documents
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Document
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search documents..."
            className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <Button variant="outline">Filter</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Document Library</CardTitle>
          <CardDescription>
            All your documents in one place
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <FileText className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-medium text-foreground">{doc.name}</h3>
                    <p className="text-sm text-muted-foreground">{doc.type}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <p className="text-sm font-medium text-foreground">{doc.target}</p>
                    <p className="text-xs text-muted-foreground">Target</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-foreground">{doc.unit}</p>
                    <p className="text-xs text-muted-foreground">Unit</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-foreground">{doc.reviewer}</p>
                    <p className="text-xs text-muted-foreground">Reviewer</p>
                  </div>
                  <div className="text-center">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      doc.status === 'Done' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
                    }`}>
                      {doc.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

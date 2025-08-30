import { useState } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Upload } from 'lucide-react';
import { toast } from 'sonner';

export function UploadTab({ onUploadSuccess, apiBaseUrl, summary, references }) {
  const [files, setFiles] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    if (!files || files.length === 0) {
      toast('Error', { description: 'Please select at least one PDF file.', style: { background: '#ef4444', color: 'white' } });
      return;
    }
    setUploading(true);
    const formData = new FormData();
    Array.from(files).forEach(file => formData.append('files', file));

    try {
      const res = await axios.post(`${apiBaseUrl}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const data = res.data;
      if (data.ok) {
        onUploadSuccess(data.files, data.summary, data.chunks);
      } else {
        toast('Upload Failed', {
          description: data.error || 'Unknown error occurred',
          style: { background: '#ef4444', color: 'white' },
        });
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message || 'Failed to connect to the server.';
      toast('Error', {
        description: errorMsg,
        style: { background: '#ef4444', color: 'white' },
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload PDFs</CardTitle>
      </CardHeader>
      <CardContent>
        <Input
          type="file"
          multiple
          accept=".pdf"
          onChange={e => setFiles(e.target.files)}
          disabled={uploading}
        />
        <Button
          onClick={handleUpload}
          disabled={uploading || !files}
          className="mt-4"
        >
          <Upload className="mr-2 h-4 w-4" /> {uploading ? 'Uploading...' : 'Upload'}
        </Button>
        {summary && (
          <div className="mt-6">
            <h3 className="text-xl font-semibold">Document Summary</h3>
            <p className="mt-2 whitespace-pre-wrap">{summary}</p>
            <Accordion type="single" collapsible className="mt-4">
              <AccordionItem value="references">
                <AccordionTrigger>References (Sample Chunks)</AccordionTrigger>
                <AccordionContent>
                  {references.map((ref, idx) => (
                    <p key={idx} className="mb-2 border-l-4 border-gray-300 pl-4">{ref}</p>
                  ))}
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
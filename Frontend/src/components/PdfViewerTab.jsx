import { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

export function PdfViewerTab({ uploadedFiles }) {
  const [numPages, setNumPages] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  // Note: PDFs are saved on backend; assume accessible via /uploads/<filename>.
  // In production, serve uploads via a backend route.

  return (
    <Card>
      <CardHeader>
        <CardTitle>View Uploaded PDFs</CardTitle>
      </CardHeader>
      <CardContent>
        <Select onValueChange={setSelectedFile}>
          <SelectTrigger>
            <SelectValue placeholder="Select a PDF" />
          </SelectTrigger>
          <SelectContent>
            {uploadedFiles.map((file) => (
              <SelectItem key={file} value={file}>
                {file}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {selectedFile && (
          <ScrollArea className="h-[600px] mt-4">
            <Document
              file={`/uploads/${selectedFile}`} // Adjust path
              onLoadSuccess={({ numPages }) => setNumPages(numPages)}
            >
              {Array.from(new Array(numPages), (_, index) => (
                <Page key={`page_${index + 1}`} pageNumber={index + 1} />
              ))}
            </Document>
          </ScrollArea>
        )}
        <p className="text-sm text-muted-foreground mt-2">
          Note: Highlighting not implemented as backend lacks page metadata.
          References shown as text chunks in chat/summary.
        </p>
      </CardContent>
    </Card>
  );
}

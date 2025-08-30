import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { UploadTab } from './components/UploadTab'
import { ChatTab } from './components/ChatTab'
import { SettingsTab } from './components/SettingsTab'
import { PdfViewerTab } from './components/PdfViewerTab'
import { toast } from 'sonner'  // Import sonner

const API_BASE_URL = 'http://127.0.0.1:8000'  // Backend URL

function App() {
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [summary, setSummary] = useState('')
  const [references, setReferences] = useState([])  // For chunk references in summary/chat

  const handleUploadSuccess = (files, newSummary, chunks) => {
    setUploadedFiles(files)
    setSummary(newSummary)
    // Simulate references for summary (since backend doesn't return chunks, we fetch sample via /chunks)
    fetchReferences()
    toast('Upload Successful', {
      description: `Processed ${files.length} files into ${chunks} chunks.`,
    })
  }

  const fetchReferences = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/chunks`)
      const data = await res.json()
      setReferences(data.sample || [])
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <header className="mb-6">
        <h1 className="text-3xl font-bold text-center">Study Assistant</h1>
      </header>
      <Tabs defaultValue="upload" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="upload">Upload PDFs</TabsTrigger>
          <TabsTrigger value="chat">Chat</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
          <TabsTrigger value="view">View PDFs</TabsTrigger>
        </TabsList>
        <TabsContent value="upload">
          <UploadTab
            onUploadSuccess={handleUploadSuccess}
            apiBaseUrl={API_BASE_URL}
            summary={summary}
            references={references}
          />
        </TabsContent>
        <TabsContent value="chat">
          <ChatTab apiBaseUrl={API_BASE_URL} />
        </TabsContent>
        <TabsContent value="settings">
          <SettingsTab apiBaseUrl={API_BASE_URL} />
        </TabsContent>
        <TabsContent value="view">
          <PdfViewerTab uploadedFiles={uploadedFiles} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default App
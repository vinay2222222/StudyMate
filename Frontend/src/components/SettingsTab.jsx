import { useEffect, useState } from 'react'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { toast } from 'sonner'

export function SettingsTab({ apiBaseUrl }) {
  const [settings, setSettings] = useState(null)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const res = await axios.get(`${apiBaseUrl}/settings`)
      setSettings(res.data)
    } catch (err) {
      toast(err, {
        description: 'Failed to load settings.',
        style: { background: '#ef4444', color: 'white' },
      })
    }
  }

  const handleUpdate = async () => {
    if (!settings) return
    try {
      const res = await axios.post(`${apiBaseUrl}/settings`, settings)
      if (res.data.ok) {
        toast('Settings Updated')
      }
    } catch (err) {
      toast(err, {
        description: 'Failed to update settings.',
        style: { background: '#ef4444', color: 'white' },
      })
    }
  }

  const handleReset = async () => {
    try {
      await axios.post(`${apiBaseUrl}/reset`)
      toast('Reset Successful')
      fetchSettings()
    } catch (err) {
      toast(err, {
        description: 'Failed to reset.',
        style: { background: '#ef4444', color: 'white' },
      })
    }
  }

  if (!settings) return <div>Loading...</div>

  return (
    <Card>
      <CardHeader>
        <CardTitle>Settings</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label>Mode</Label>
          <Select
            value={settings.mode}
            onValueChange={value => setSettings({ ...settings, mode: value })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="topic">Topic</SelectItem>
              <SelectItem value="fixed">Fixed</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {settings.mode === 'topic' && (
          <div>
            <Label>Similarity Threshold ({settings.similarity_threshold})</Label>
            <Slider
              value={[settings.similarity_threshold * 100]}
              onValueChange={([value]) => setSettings({ ...settings, similarity_threshold: value / 100 })}
              max={100}
              step={1}
            />
          </div>
        )}
        {settings.mode === 'fixed' && (
          <>
            <div>
              <Label>Chunk Size</Label>
              <Input
                type="number"
                value={settings.chunk_size}
                onChange={e => setSettings({ ...settings, chunk_size: +e.target.value })}
              />
            </div>
            <div>
              <Label>Chunk Overlap</Label>
              <Input
                type="number"
                value={settings.chunk_overlap}
                onChange={e => setSettings({ ...settings, chunk_overlap: +e.target.value })}
              />
            </div>
          </>
        )}
        <div>
          <Label>Top K</Label>
          <Input
            type="number"
            value={settings.top_k}
            onChange={e => setSettings({ ...settings, top_k: +e.target.value })}
          />
        </div>
        <div>
          <Label>Model ID</Label>
          <Input
            value={settings.model_id}
            onChange={e => setSettings({ ...settings, model_id: e.target.value })}
          />
        </div>
        <Button onClick={handleUpdate}>Save Settings</Button>
        <Button variant="destructive" onClick={handleReset} className="ml-4">Reset All</Button>
      </CardContent>
    </Card>
  )
}
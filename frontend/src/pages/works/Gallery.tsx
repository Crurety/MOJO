import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Button, EmptyState, PageHeader, SurfaceCard } from '../../components'
import { useContent } from '../../hooks/useContent'
import { useI18n } from '../../i18n'

type GalleryWork = {
  id: number
  title?: string | null
  work_type: string
  file_url?: string
  thumbnail_url?: string | null
  created_at: string
}

const Gallery = () => {
  const { t } = useI18n()
  const { fetchGallery, loading } = useContent()
  const [items, setItems] = useState<GalleryWork[]>([])

  useEffect(() => {
    const load = async () => {
      const response = await fetchGallery(0, 24)
      if (response.success) {
        setItems((response.data || []) as GalleryWork[])
      }
    }
    void load()
  }, [])

  return (
    <div className="space-y-6 text-[#e8f4ff]">
      <PageHeader
        eyebrow={t('page.gallery.title')}
        title={t('nav.gallery')}
        description={t('page.gallery.desc')}
        actions={<Link to="/pricing"><Button variant="secondary">{t('home.readyPlans')}</Button></Link>}
      />

      {items.length === 0 && !loading ? (
        <EmptyState title={t('page.gallery.title')} description={t('page.gallery.desc')} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {items.map((item) => (
            <SurfaceCard key={item.id} className="overflow-hidden p-0">
              <div className="aspect-[4/3] border-b border-[rgba(132,179,219,0.18)] bg-[rgba(5,16,30,0.9)]">
                {item.thumbnail_url || item.file_url ? (
                  <img
                    src={item.thumbnail_url || item.file_url}
                    alt={item.title || item.work_type}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full items-center justify-center text-sm text-[#89a9c4]">{item.work_type}</div>
                )}
              </div>
              <div className="p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{item.work_type}</p>
                <h3 className="mt-2 text-lg font-semibold text-[#f2fbff]">{item.title || t('page.gallery.title')}</h3>
                <p className="mt-2 text-sm text-[#8eb1ce]">{new Date(item.created_at).toLocaleString()}</p>
                {item.file_url ? (
                  <a href={item.file_url} target="_blank" rel="noreferrer" className="mt-4 inline-flex text-sm font-semibold text-[#88dcff] hover:text-[#dff8ff]">
                    {t('tasks.table.view')}
                  </a>
                ) : null}
              </div>
            </SurfaceCard>
          ))}
        </div>
      )}
    </div>
  )
}

export default Gallery

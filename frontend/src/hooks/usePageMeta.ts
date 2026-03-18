import { useEffect } from 'react'

const BASE_URL = 'https://partner-scout.vercel.app'
const DEFAULT_TITLE = 'PartnerScout AI'
const DEFAULT_DESCRIPTION =
  'AI-powered Instagram partner discovery for D2C brands. Discover, score, and connect with ideal collaborators in minutes.'

interface PageMeta {
  title: string
  description: string
  keywords?: string
  canonical?: string
}

function setMetaTag(attr: string, key: string, content: string) {
  let el = document.querySelector(`meta[${attr}="${key}"]`) as HTMLMetaElement | null
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function setCanonical(path: string) {
  const url = path.startsWith('http') ? path : `${BASE_URL}${path}`
  let el = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', 'canonical')
    document.head.appendChild(el)
  }
  el.setAttribute('href', url)
}

export function usePageMeta({ title, description, keywords, canonical }: PageMeta) {
  useEffect(() => {
    // Title
    document.title = title

    // Standard meta
    setMetaTag('name', 'description', description)
    if (keywords) {
      setMetaTag('name', 'keywords', keywords)
    }

    // Open Graph
    setMetaTag('property', 'og:title', title)
    setMetaTag('property', 'og:description', description)
    if (canonical) {
      const url = canonical.startsWith('http') ? canonical : `${BASE_URL}${canonical}`
      setMetaTag('property', 'og:url', url)
    }

    // Canonical
    if (canonical) {
      setCanonical(canonical)
    }

    // Restore defaults on unmount
    return () => {
      document.title = DEFAULT_TITLE
      setMetaTag('name', 'description', DEFAULT_DESCRIPTION)
    }
  }, [title, description, keywords, canonical])
}

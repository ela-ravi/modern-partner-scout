import React, { createContext, useEffect, useState } from 'react'
import { type Session, type User } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'

export type AuthContextType = {
    session: Session | null
    user: User | null
    loading: boolean
    signInWithPassword: (email: string, password: string) => Promise<{ error: any }>
    signOut: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [session, setSession] = useState<Session | null>(null)
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // Get initial session
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session)
            setUser(session?.user ?? null)
            setLoading(false)
        })

        // Listen for changes
        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session)
            setUser(session?.user ?? null)
            setLoading(false)
        })

        return () => subscription.unsubscribe()
    }, [])

    const signInWithPassword = async (email: string, password: string) => {
        const { error } = await supabase.auth.signInWithPassword({
            email,
            password,
        })
        return { error }
    }

    const signOut = async () => {
        await supabase.auth.signOut()
    }

    const value = {
        session,
        user,
        loading,
        signInWithPassword,
        signOut,
    }

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

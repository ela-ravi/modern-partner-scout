import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '@/contexts/AuthContext'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/components/ui/Toast'

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

const signupSchema = z
  .object({
    email: z.string().email('Please enter a valid email address'),
    password: z.string().min(6, 'Password must be at least 6 characters'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  })

type LoginFormData = z.infer<typeof loginSchema>
type SignupFormData = z.infer<typeof signupSchema>

export default function LoginPage() {
  const [isSignUp, setIsSignUp] = useState(false)
  const { signIn, signUp } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const toast = useToast()

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/dashboard'

  // Login form
  const loginForm = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  // Signup form
  const signupForm = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
  })

  const currentForm = isSignUp ? signupForm : loginForm
  const { reset } = currentForm

  const onLoginSubmit = async (data: LoginFormData) => {
    try {
      await signIn(data.email, data.password)
      toast.success('Welcome back!')
      navigate(from, { replace: true })
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Authentication failed')
    }
  }

  const onSignupSubmit = async (data: SignupFormData) => {
    try {
      await signUp(data.email, data.password)
      toast.success('Account created! Please check your email to verify.')
      setIsSignUp(false)
      loginForm.reset()
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Authentication failed')
    }
  }

  return (
    <Card className="animate-fade-in">
      <h2 className="text-xl font-semibold text-apple-text mb-6">
        {isSignUp ? 'Create an account' : 'Sign in to your account'}
      </h2>

      {isSignUp ? (
        <form onSubmit={signupForm.handleSubmit(onSignupSubmit)} className="space-y-4">
          <Input
            label="Email"
            type="email"
            autoComplete="email"
            error={signupForm.formState.errors.email?.message}
            {...signupForm.register('email')}
          />

          <Input
            label="Password"
            type="password"
            autoComplete="new-password"
            error={signupForm.formState.errors.password?.message}
            {...signupForm.register('password')}
          />

          <Input
            label="Confirm Password"
            type="password"
            autoComplete="new-password"
            error={signupForm.formState.errors.confirmPassword?.message}
            {...signupForm.register('confirmPassword')}
          />

          <Button type="submit" className="w-full" loading={signupForm.formState.isSubmitting}>
            Create Account
          </Button>
        </form>
      ) : (
        <form onSubmit={loginForm.handleSubmit(onLoginSubmit)} className="space-y-4">
          <Input
            label="Email"
            type="email"
            autoComplete="email"
            error={loginForm.formState.errors.email?.message}
            {...loginForm.register('email')}
          />

          <Input
            label="Password"
            type="password"
            autoComplete="current-password"
            error={loginForm.formState.errors.password?.message}
            {...loginForm.register('password')}
          />

          <Button type="submit" className="w-full" loading={loginForm.formState.isSubmitting}>
            Sign In
          </Button>
        </form>
      )}

      <div className="mt-6 text-center">
        <button
          type="button"
          onClick={() => {
            setIsSignUp(!isSignUp)
            reset()
          }}
          className="text-sm text-apple-blue hover:underline"
        >
          {isSignUp ? 'Already have an account? Sign in' : "Don't have an account? Sign up"}
        </button>
      </div>
    </Card>
  )
}

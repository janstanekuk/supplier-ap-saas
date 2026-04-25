import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <h1>Supplier AP Contract Manager</h1>
      <p>Welcome! This is your SaaS frontend.</p>
      <button onClick={() => setCount((count) => count + 1)}>
        Test button: {count}
      </button>
    </div>
  )
}

export default App
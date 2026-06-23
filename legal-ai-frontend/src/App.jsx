import { useState } from 'react'

import './App.css'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import ProtectedRoutes from './component/ProtectedRoutes'
import Ask from './pages/Ask'
import Upload from './pages/Upload'
import Navbar from './component/Navbar'
import Sidebar from './component/Sidebar'
import History from './pages/History'

function App() {

  return (
    <BrowserRouter>
    <Navbar/>
    {/* <Sidebar/> */}
    <Routes>
      <Route path='/' element={<Login/>}  />
      <Route path='/register' element={<Register/>}  />
      <Route  path='/ask' element={
        <ProtectedRoutes><Ask/></ProtectedRoutes>
      } />
      <Route  path='/upload' element={
        <ProtectedRoutes><Upload/></ProtectedRoutes>
      } />
      <Route  path='/history' element={
        <ProtectedRoutes><History/></ProtectedRoutes>
      } />
    </Routes>
    </BrowserRouter>
  )
}

export default App

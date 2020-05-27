import React,{Component,useState,useEffect} from 'react';

const Login=()=>{
const [email,setEmail]=useState('')
const [password,setPassword]=useState('')
const handleChange=(event)=>{
	if (event.target.name=='email'){
		setEmail(event.target.value)

	}
	else if(event.target.name=='password'){
	setPassword(event.target.value)
	}

}

	return(<div className='login-form'>
		<legend>Login</legend>
<form action='auth/login' method='post'>
	<label className='input' for='email'>Email</label>

	<input className='input' autofocus onChange={handleChange} id= 'email' name='email' value={email} type='email'/>
	<label for='password'>Password</label>

	<input className='input' onChange={handleChange} id= 'password' value={password} name='password' type='password'/>
	
	<button className='button' type='submit'  >Login</button>
	</form>
</div>
);}

export default Login;


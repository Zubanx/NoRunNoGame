`use strict`

const distance = document.getElementById("distanceToday")
const userName = document.getElementById("userName")

async function getUser(){
    try{
        const response = await fetch("http://127.0.0.1:8000/user")
        if(!response.ok){
            throw new Error(`Http error! status: ${response.status}`)
        }
        const userData = await response.json() 
        
        const firstName = userData['firstname']
        const lastName = userData['lastname']
        const fullName = firstName + " " + lastName
        console.log(fullName)
        userName.textContent = fullName
    }catch (error){
        console.log("Error fetching user:", error)
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    await getUser(); // Load user data when page is ready
});
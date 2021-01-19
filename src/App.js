import Header from "./components/Header";
import {useState } from "react";
import Tasks from "./components/Tasks";
function App (){
    const [tasks, setTasks] =useState([
         {
            id:1,
            text: "doctors Appointment,",
            day:"March 12 at 1:00pm",
            reminder:true,
        },
         {
            id:2,
            text: "Business Presentation",
            day:"April 15 at 3:00pm",
            reminder:true,
        },
         {
            id:3,
            text: "Boot-camp demo",
            day:"March 23 at 5:00pm",
            reminder:true,
        },
    ])
    return(
          <div className="container">
              <Header/> 
             <Tasks tasks={tasks}/>
          </div>  
       
    )
}

export default App;
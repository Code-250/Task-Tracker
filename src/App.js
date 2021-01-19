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

    //               delete Task         \\

    const deleteTask = (id)=>{
        setTasks(tasks.filter((task)=>
        task.id !== id))
    }
    return(
          <div className="container">
              <Header/> 
             {tasks.length >0 ? (<Tasks 
             tasks={tasks} 
             onDelete={deleteTask}/>
             ) :(
                 "No Task To Show"
             )}
          </div>  
       
    )
}

export default App;
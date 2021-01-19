import Header from "./components/Header";
import {useState } from "react";
import Tasks from "./components/Tasks";
import AddTask from "./components/AddTask";
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

    //             ToggleReminder         \\

    const toggleReminder = (id) =>{
        setTasks(tasks.map((task)=> 
        task.id === id ? {...task,
        reminder : !task.reminder} 
        : task ))
    }
    
    return(
          <div className="container">
              <Header/>
              <AddTask /> 
             {tasks.length >0 ? (<Tasks 
             tasks={tasks} 
             onDelete={deleteTask}
             onToggle={toggleReminder}/>
             ) :(
                 "No Task To Show"
             )}
          </div>  
       
    )
}

export default App;
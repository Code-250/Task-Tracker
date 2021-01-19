import Button from "./Button";
import propTypes from "prop-types"
import "../index.css";

const Header =({title, showAdd, onAdd})=>{
   
    return(
        <div className="header">
            <h1 className="title">{title}</h1>
            <Button  text={!showAdd ? "Add" :  "close"} 
             color={!showAdd ? "indigo" : "red"}
            onClick={onAdd}/>
        </div>
    )
}
Header.defaultProps={
    title:"Task Tracking",
    
}
Header.propTypes = {
    title:propTypes.string
}
export default Header;
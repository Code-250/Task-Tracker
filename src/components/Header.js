import Button from "./Button";
import propTypes from "prop-types"
import "../index.css";

const Header =({title, text,color})=>{
    return(
        <div className="header">
            <header className="title">{title}</header>
            <Button  text={text} color={color}/>
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
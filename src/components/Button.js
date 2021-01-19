import propTypes from "prop-types";

const Button =({ onClick,text, color })=>{
  return <button onClick={onClick} style={{backgroundColor:color}} className="btn">{text} </button>
  
    
}


Button.propTypes ={
  text:propTypes.string,
  color:propTypes.string
}
export default Button;
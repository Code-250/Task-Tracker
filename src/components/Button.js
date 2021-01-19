import propTypes from "prop-types";

const Button =({text, color})=>{
  return <button style={{backgroundColor: color}} className="btn">{text} </button>
  
    
}
Button.defaultProps ={
  text:"hello",
  color:"indigo"
}

Button.propTypes ={
  text:propTypes.string,
  color:propTypes.string
}
export default Button;
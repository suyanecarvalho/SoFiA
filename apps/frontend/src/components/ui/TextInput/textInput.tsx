import { ReactNode } from "react";
import "../TextInput/textInput.css"

const TextInput = ({ children }: { children: ReactNode }) => {
    return (
        <input className="textInputStyle" type="text" placeholder={children as string} />
    );
};

export default TextInput;
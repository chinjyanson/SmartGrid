import React, { useEffect } from 'react';
import teamMembers from "./teamMembers";

const About = () => {
    useEffect(() => {
        document.title = 'About | Smart Grid';
    }, []);

    return (
        <div className="about">
            <div>
                <h1 style={{ color: 'white' }}>About</h1>
                <p style={{ color: 'white' }}>Project description goes here...</p>
                {/* <div>
                    {teamMembers.map((member, index) => (
                        <div key={index}>
                            <h2 style={{ color: 'white' }}>{member.name}</h2>
                            <p style={{ color: 'white' }}>{member.bio}</p>
                        </div>
                    ))}
                </div> */}
            </div>
        </div>
    );
};

export default About;

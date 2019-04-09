function jtrim(text) {
    const rtrim = /^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g;
    return text == null ?
        '' :
        (text + '').replace(rtrim, '');
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie != '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = jtrim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function loginWithAuthenticate(scatter, requiredFields, login_url, onSignatureFail, onSignatureSuccess,
    onLoginRequestError, onLoginFail, onLoginSuccess) {
        scatter.getIdentity(requiredFields).then(identity => {
            if (identity) {
                const getRandom = () => Math.round(Math.random() * 8 + 1).toString();
                let nonce = '';
                for(let i = 0; i < 12; i++) nonce += getRandom();

                const publicKey = identity.publicKey;
                const toSign = 'helloworldiamtheonethatknocks'

                scatter.authenticate(nonce, toSign, publicKey).then(res => {
                    if (typeof onSignatureSuccess === 'function') {
                        onSignatureSuccess(res);
                    }
                    const request = new XMLHttpRequest();
                    request.open('POST', login_url, true);
                    request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
                    request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));            
                    request.onload = function () {
                        if (request.status >= 200 && request.status < 400) {
                            // Success!
                            const resp = JSON.parse(request.responseText);
                            if (resp.success && typeof onLoginSuccess === 'function') {
                                onLoginSuccess(resp);
                            } else if (typeof onLoginFail === 'function') {
                                onLoginFail(resp);
                            }
                        } else {
                            // We reached our target server, but it returned an error
                            console.log('Scatter login failed - request status ' + request.status);
                            if (typeof onLoginRequestError === 'function') {
                                onLoginRequestError(request);
                            }
                        }
                    };
                    request.onerror = function () {
                        console.log('Scatter login failed - there was an error');
                        if (typeof onLoginRequestError === 'function') {
                            onLoginRequestError(request);
                        }
                        // There was a connection error of some sort
                    };
                    const formData = '&nonce=' + nonce + '&public_key=' + publicKey + '&res=' + res
                    request.send(formData);

                }).catch(signatureError => {
                    if (typeof onSignatureFail === 'function') {
                        onSignatureFail(signatureError);
                    }
                })

            } else {
                console.log('Identity not found, have to signup')
            }
        });
    }


function signupWithData(scatter, signup_url, onSignupRequestError, onSignupSuccess, onSignupFail) {
    scatter.getIdentity(requiredFields).then(identity => {
        if (identity) {
            const request = new XMLHttpRequest();
            request.open('POST', signup_url, true);
            request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
            request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            const formData = '&publicKey=' + identity.publicKey;
            request.onload = function () {
                if (request.status >= 200 && request.status < 400) {
                    // Success!
                    const resp = JSON.parse(request.responseText);
                    if (resp.success) {
                        if (typeof onSignupSuccess === 'function') {
                            onSignupSuccess(resp);
                        }
                    } else {
                        if (typeof onSignupFail === 'function') {
                            onSignupFail(resp);
                        }
                    }
                } else {
                    // We reached our target server, but it returned an error
                    console.log('Signup failed - request status ' + request.status);
                    if (typeof onSignupRequestError === 'function') {
                        onSignupRequestError(request);
                    }
                }
            };
            request.onerror = function () {
                console.log('Signup failed - there was an error connecting to the server');
                if (typeof onSignupRequestError === 'function') {
                    onSignupRequestError(request);
                }
            };
            request.send(formData);
        } else console.log('identity not found, have to signup')
    })
}


async function requestIdentity(requiredFields, pubkeyFieldName, signup_url, network, onIdentityReject) {
    let identitySettings = {
        personal: requiredFields,
    };
    if (network) {
        await scatter.suggestNetwork(network);
        identitySettings['accounts'] = network;
    }

    scatter.getIdentity(identitySettings).then((identity) => {
        signupWithData(identity.publicKey, pubkeyFieldName, identity.personal.email, signup_url, console.log, console.log, console.log)
    }).catch(error => {
        console.log('Identity or Network was rejected');
        if (typeof onIdentityReject === 'function') {
            onIdentityReject(error);
        }
    })
}

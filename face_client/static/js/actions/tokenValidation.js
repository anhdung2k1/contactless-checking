function isTokenValid() {
    // Retrieve profile data from localStorage
    const tokenData = JSON.parse(localStorage.getItem('profile'));

    // Check if tokenData exists and has an expireDate
    if (tokenData && tokenData.expireDate) {
        // Convert expireDate to timestamp in seconds
        const tokenDateExp = Math.floor(Date.parse(tokenData.expireDate) / 1000);

        // Get current timestamp in seconds
        const currentTimestampSeconds = Math.floor(Date.now() / 1000);

        // Compare token expiry time with current time
        console.log("tokenDateExp: ", tokenDateExp);
        console.log("currentTimestampSeconds: ", currentTimestampSeconds);
        console.log(tokenDateExp >= currentTimestampSeconds);
        return tokenDateExp >= currentTimestampSeconds;
    } else {
        return false; // Return false if tokenData or expireDate is missing
    }
}

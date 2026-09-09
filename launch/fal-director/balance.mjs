// Read-only balance check; requires a fal key with billing permission.
const response=await fetch('https://api.fal.ai/v1/account/billing?expand=credits',{
 headers:{Authorization:`Key ${process.env.FAL_KEY}`},signal:AbortSignal.timeout(20000)
});
const data=await response.json();
console.log(JSON.stringify({status:response.status,credits:data.credits??null,error:data.error?.message??data.detail??null}));

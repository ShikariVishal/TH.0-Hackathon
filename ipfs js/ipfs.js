import ipfsClient from 'ipfs-http-client'

{/* <script type="module" src="node_modules\ipfs-http-client\src\"></script> */}

let ipfs = ipfsClient({ host: 'ipfs.infura.io', port: '5001', protocol: 'https' })
const infura = 'https://ipfs.infura.io:5001/api/v0'

data = 'shikari vishal'

ipfs.add(data, (error, result)=> {
    console.log(result)
    if(error){
        console.error(error)
        return
    }
    else {

    }
})

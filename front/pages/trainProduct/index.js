import { useState, useEffect } from 'react';

export default function Home() {
  const [products, setProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [webcamStream, setWebcamStream] = useState(null);
  const [productName, setProductName] = useState('');

  useEffect(() => {
    fetchProducts();
    startWebcam();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch('http://localhost:5000/get_products');
      const data = await response.json();
      setProducts(data.products);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const searchProducts = async (query) => {
    try {
      const response = await fetch(`http://localhost:5000/search_products?query=${query}`);
      const data = await response.json();
      setProducts(data.products);
    } catch (error) {
      console.error('Error searching products:', error);
    }
  };

  const handleSearch = () => {
    searchProducts(searchQuery);
  };

  const handleCapture = async () => {
    if (!productName) {
      alert('Please enter a product name.');
      return;
    }

    const canvas = document.createElement('canvas');
    const videoElement = document.querySelector('video');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

    const base64Image = canvas.toDataURL('image/png');

    // Send the captured image to backend
    const response = await fetch('http://localhost:5000/capture_new_product_image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_name: productName, image: base64Image }),
    });

    const data = await response.json();
    console.log(data.message);
  };

  const startWebcam = () => {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        setWebcamStream(stream);
        document.querySelector('video').srcObject = stream;
      })
      .catch((error) => console.error('Error accessing webcam:', error));
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-2xl font-bold text-center mb-6">Product Capture System</h1>

      {/* Search Bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search Products..."
          className="w-full p-2 border border-gray-300 rounded"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button
          onClick={handleSearch}
          className="bg-blue-500 text-white p-2 rounded mt-2"
        >
          Search
        </button>
      </div>

      {/* Product List */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {products.map((product, index) => (
          <div
            key={index}
            className="p-4 bg-white border border-gray-300 rounded"
          >
            {product}
          </div>
        ))}
      </div>

      {/* Product Name Input */}
      <div className="mt-6">
        <label htmlFor="productName" className="block text-lg">Enter Product Name:</label>
        <input
          type="text"
          id="productName"
          placeholder="Product Name"
          className="p-2 border border-gray-300 rounded mt-2"
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
        />
      </div>

      {/* Webcam Section */}
      <div className="mt-6">
        <video className="w-full" autoPlay></video>
        <button
          onClick={handleCapture}
          className="mt-4 bg-green-500 text-white p-2 rounded"
        >
          Capture Image
        </button>
      </div>
    </div>
  );
}

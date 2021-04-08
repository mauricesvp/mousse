export default async function runRequest(body, facets, filters) {
  const response = await fetch("https://tu.eno.pw/api/v0/select?" + new URLSearchParams(body) + filters, {
    method: "GET",
    headers: { "content-type": "application/json" },
  });
  return response.json();
}

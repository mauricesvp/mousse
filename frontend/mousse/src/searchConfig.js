import buildRequest from "./buildRequest";
import runRequest from "./runRequest";
import buildState from "./buildState";

const config = {
    debug: true,
    hasA11yNotifications: true,
    alwaysSearchOnInitialLoad: true,
    onSearch: async state => {
        const { resultsPerPage } = state;
        const { body, facets, filters} = buildRequest(state);
        const responseJson = await runRequest(body, facets, filters);
        const finalState = buildState(responseJson, resultsPerPage);
        console.log(finalState);
        return finalState;
    }
};

export default config;
